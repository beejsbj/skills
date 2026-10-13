"""The established question banks. Burooj's rule: never shorten or replace them.

They are sent folded (Telegram expandable blockquote) under the opener, so the
full bank is always present without filling the chat.
"""

MORNING = [
    "How did you sleep?",
    "How are you feeling — physically, mentally, emotionally?",
    "What's on your chest right now?",
    "Which of your values will you experiment with today?",
    "What's your centering mantra?",
    "Two things you're grateful for — why?",
    "Top priority today?",
    "2-3 supporting goals for a successful day?",
    "Any worries about the day ahead? What's the plan?",
    "Who needs your support today? How will you show up?",
    "What would make today deeply satisfying?",
]

EVENING = [
    ("Brain Dump & Letting Go", ["What's spinning in your mind?", "What do you need to release before sleep?"]),
    ("Day Review", ["What went well today?", "What challenged you?", "What did you learn?"]),
    ("Story-Worthy Moments", [
        "What interesting moments happened, even if small?",
        "What made you smile or laugh?",
        "What surprised you?",
    ]),
    ("Wins & Celebrations", ["What wins, big or small, did you experience?", "What are you proud of?"]),
    ("Insights & Revelations", [
        "What realizations or new understandings emerged?",
        "What did you learn about yourself or others?",
    ]),
    ("Values & Alignment", ["How did you honor your values today?", "Where did you feel most/least aligned?"]),
    ("Energy Awareness", ["What energized you today?", "What drained your energy?"]),
    ("Connection Reflection", [
        "What attention bids did you notice?",
        "Which connections did you lean into?",
        "Who showed up for you, and who did you show up for?",
    ]),
    ("Gratitude", ["What moments from today are you thankful for?", "What simple joys touched you today?"]),
    ("Peace & Calming", [
        "What brought you peace today?",
        "What's one thing you can appreciate about yourself?",
        "What do you want to carry into your sleep?",
    ]),
]

MIDWEEK = [
    ("Energy Check", ["How's your energy been this week?", "High/low/variable? Any idea why?"]),
    ("Drift Check", [
        "Monday's intentions vs. where you are now — aligned or drifted?",
        "Anything taking you off course?",
    ]),
    ("Support Check", ["What do you need this week?", "Who can help? What would help?"]),
]

WEEKLY = [
    ("Energy & Themes", [
        "Which days had energy, which didn't — and what was behind it?",
        "What kept coming up across the week?",
    ]),
    ("Values & Alignment", ["Which values showed up this week? Which were neglected?"]),
    ("Dropped Threads", ["What intentions or promises slipped — to yourself or others?"]),
    ("Wins", ["What's worth celebrating from the week, even small?"]),
    ("Connections", ["Who showed up for you, and who did you show up for?"]),
    ("Forward", [
        "What do you want to carry forward from this week?",
        "What thread do you want to pull next week?",
        "What would make next week feel aligned?",
    ]),
]

TITLES = {
    "morning": "Morning journal",
    "evening": "Evening journal",
    "midweek": "Midweek check-in",
    "weekly": "Weekly pattern scan",
    "note": "Journal note",
}


def bank_lines(kind: str) -> list[str]:
    """Plain-text lines of the bank, numbered like the original skills."""
    if kind == "morning":
        return [f"{i}. {q}" for i, q in enumerate(MORNING, 1)]
    sections = {"evening": EVENING, "midweek": MIDWEEK, "weekly": WEEKLY}[kind]
    lines: list[str] = []
    for i, (title, qs) in enumerate(sections, 1):
        lines.append(f"{i}. {title}")
        lines.extend(f"   • {q}" for q in qs)
    return lines


def bank_text(kind: str) -> str:
    return "\n".join(bank_lines(kind))
