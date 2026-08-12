from __future__ import annotations

import importlib.util
import io
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts" / "cockpit.py"
SPEC = importlib.util.spec_from_file_location("cockpit_under_test", SCRIPT)
assert SPEC and SPEC.loader
cockpit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cockpit)


class TrackerPrimitiveTests(unittest.TestCase):
    def test_child_creation_emits_parent_and_assignee_ids(self) -> None:
        response = {
            "issueCreate": {
                "success": True,
                "issue": {"id": "new", "identifier": "BJS-3", "title": "Child"},
            }
        }
        with (
            patch.object(cockpit, "linear_team_metadata", return_value={"id": "team"}),
            patch.object(cockpit, "linear_issue_uuid", return_value="parent-uuid"),
            patch.object(cockpit, "linear_user_id", return_value="user-uuid"),
            patch.object(cockpit, "run_linear_graphql", return_value=response) as graphql,
        ):
            cockpit.create_issue_with_app_actor(
                "Child",
                parent="BJS-1",
                assignee="dev@example.com",
            )

        variables = graphql.call_args.args[1]
        self.assertEqual(variables["input"]["parentId"], "parent-uuid")
        self.assertEqual(variables["input"]["assigneeId"], "user-uuid")

    def test_machine_readable_issue_preserves_graph_and_comments(self) -> None:
        issue = {
            "id": "map-uuid",
            "identifier": "BJS-1",
            "updatedAt": "2026-08-12T12:00:00.000Z",
            "assignee": {"id": "dev"},
            "children": {
                "nodes": [
                    {"id": "c2", "subIssueSortOrder": 20},
                    {"id": "c1", "subIssueSortOrder": 10},
                ],
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            },
            "relations": {
                "nodes": [{"id": "out"}],
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            },
            "inverseRelations": {
                "nodes": [{"id": "in"}],
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            },
        }
        with (
            patch.object(cockpit, "run_linear_graphql", return_value={"issue": issue}),
            patch.object(cockpit, "load_issue_comments_graphql", return_value=[{"id": "comment"}]),
        ):
            loaded = cockpit.load_linear_issue_tracker_graphql("BJS-1")

        self.assertEqual([node["id"] for node in loaded["children"]["nodes"]], ["c1", "c2"])
        self.assertEqual(loaded["relations"]["nodes"][0]["id"], "out")
        self.assertEqual(loaded["inverseRelations"]["nodes"][0]["id"], "in")
        self.assertEqual(loaded["comments"][0]["id"], "comment")

    def test_machine_readable_issue_paginates_graph_connections(self) -> None:
        issue = {
            "id": "map-uuid",
            "children": {
                "nodes": [{"id": "c2", "subIssueSortOrder": 20}],
                "pageInfo": {"hasNextPage": True, "endCursor": "next"},
            },
            "relations": {"nodes": [], "pageInfo": {"hasNextPage": False}},
            "inverseRelations": {"nodes": [], "pageInfo": {"hasNextPage": False}},
        }
        next_page = {
            "nodes": [{"id": "c1", "subIssueSortOrder": 10}],
            "pageInfo": {"hasNextPage": False, "endCursor": None},
        }
        with (
            patch.object(cockpit, "run_linear_graphql", return_value={"issue": issue}),
            patch.object(cockpit, "load_issue_tracker_connection_page", return_value=next_page),
            patch.object(cockpit, "load_issue_comments_graphql", return_value=[]),
        ):
            loaded = cockpit.load_linear_issue_tracker_graphql("BJS-1")

        self.assertEqual([node["id"] for node in loaded["children"]["nodes"]], ["c1", "c2"])

    def test_assignment_and_unassignment_use_assignee_id(self) -> None:
        with (
            patch.object(cockpit, "linear_user_id", return_value="user-uuid"),
            patch.object(
                cockpit,
                "update_issue_with_app_actor",
                return_value={"identifier": "BJS-1"},
            ) as update,
            redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(cockpit.assign_issue_command("BJS-1", "dev@example.com"), 0)
            self.assertEqual(cockpit.assign_issue_command("BJS-1", None), 0)

        self.assertEqual(update.call_args_list[0].args[1], {"assigneeId": "user-uuid"})
        self.assertEqual(update.call_args_list[1].args[1], {"assigneeId": None})

    def test_blocks_relation_is_source_to_target_and_deletion_uses_relation_id(self) -> None:
        create_response = {
            "issueRelationCreate": {
                "success": True,
                "issueRelation": {"id": "relation-uuid", "type": "blocks"},
            }
        }
        delete_response = {"issueRelationDelete": {"success": True}}
        with (
            patch.object(cockpit, "linear_issue_uuid", side_effect=["source-uuid", "target-uuid"]),
            patch.object(cockpit, "load_issue_relations_graphql", return_value={"relations": []}),
            patch.object(cockpit, "run_linear_graphql", return_value=create_response) as graphql,
        ):
            cockpit.create_issue_relation_with_app_actor("BJS-1", "BJS-2", "blocks")

        self.assertEqual(
            graphql.call_args.args[1]["input"],
            {"issueId": "source-uuid", "relatedIssueId": "target-uuid", "type": "blocks"},
        )

        with patch.object(cockpit, "run_linear_graphql", return_value=delete_response) as graphql:
            cockpit.delete_issue_relation_with_app_actor("relation-uuid")
        self.assertEqual(graphql.call_args.args[1], {"id": "relation-uuid"})

    def test_stale_guard_performs_no_mutation(self) -> None:
        with (
            patch.object(
                cockpit,
                "load_linear_issue_graphql",
                return_value={"updatedAt": "newer"},
            ),
            patch.object(cockpit, "update_issue_with_app_actor") as update,
            redirect_stdout(io.StringIO()),
        ):
            result = cockpit.update_issue_command(
                "BJS-1",
                title="New title",
                expected_updated_at="older",
            )

        self.assertEqual(result, 3)
        update.assert_not_called()

    def test_update_read_error_is_reported(self) -> None:
        with (
            patch.object(cockpit, "load_linear_issue_graphql", side_effect=RuntimeError("offline")),
            patch.object(cockpit, "update_issue_with_app_actor") as update,
            redirect_stdout(io.StringIO()) as output,
        ):
            result = cockpit.update_issue_command(
                "BJS-1",
                title="New title",
                expected_updated_at="older",
            )

        self.assertEqual(result, 1)
        self.assertIn("Update failed: offline", output.getvalue())
        update.assert_not_called()

    def test_cli_has_no_workflow_specific_verbs(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            check=True,
            text=True,
            capture_output=True,
        )
        for forbidden in ("wayfinder-", "frontier", "claim", "map-update"):
            self.assertNotIn(forbidden, completed.stdout)


if __name__ == "__main__":
    unittest.main()
