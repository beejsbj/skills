case $- in
  *i*) ;;
  *) return 0 2>/dev/null || exit 0 ;;
esac

if [[ "$(hostname -s 2>/dev/null)" == bjslab && -z "${BJSLAB_CONTEXT_BANNER_SHOWN:-}" ]]; then
  export BJSLAB_CONTEXT_BANNER_SHOWN=1
  if command -v bjslab-context >/dev/null 2>&1; then
    bjslab-context --banner
  fi
fi
