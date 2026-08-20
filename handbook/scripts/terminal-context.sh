case $- in
  *i*) ;;
  *) return 0 2>/dev/null || exit 0 ;;
esac

if [[ "$(hostname -s 2>/dev/null)" == bjslab && -z "${HANDBOOK_BANNER_SHOWN:-}" ]]; then
  export HANDBOOK_BANNER_SHOWN=1
  if command -v handbook >/dev/null 2>&1; then
    handbook --banner
  fi
fi
