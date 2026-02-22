"""Shell script template for transparent Docker proxy."""

SHELL_TEMPLATE = """\
#!/usr/bin/env bash
# StackForDev — transparent Docker dev environment proxy
# Usage: source devrun.sh
#        devrun <command>   e.g. devrun python manage.py runserver

devrun() {{
  docker compose run --rm dev "$@"
}}

export -f devrun
echo "devrun is ready. Run: devrun <command>"
"""
