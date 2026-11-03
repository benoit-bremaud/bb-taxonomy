# Local CI: `mise x -- just check` before every push; .github/workflows/ci.yml runs the same steps.

set shell := ["sh", "-eu", "-c"]

default: check

# YAML style, spelling
lint:
    yamllint --strict .
    typos

# The registry rules, against the base branch so no ID is ever removed
registry base="origin/main":
    #!/bin/sh
    set -eu
    old=$(mktemp)
    trap 'rm -f "$old"' EXIT
    if git show {{quote(base)}}:registry.yaml > "$old" 2> /dev/null; then
      python3 scripts/check_registry.py --base "$old"
    else
      echo "registry: no registry.yaml on {{base}}, base check skipped"
      python3 scripts/check_registry.py
    fi

# Unit tests of the check script
test:
    python3 -m unittest discover -s scripts

# Secrets in the whole git history
secrets:
    gitleaks git --redact --verbose --no-banner .

check: lint registry test secrets
