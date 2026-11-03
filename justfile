# Local CI (skill local-ci): no GitHub workflow runs these checks; lefthook runs `check` on
# pre-push. Run through `mise x -- just <recipe>` when the shell does not activate mise.

set shell := ["sh", "-eu", "-c"]

default: check

# Once per clone: the pinned toolchain and the git hooks
setup:
    mise install
    mise x -- lefthook install

# YAML style, spelling
lint:
    yamllint --strict .
    typos

# The registry rules, and against the base branch: no ID removed, no slug changed
registry base="origin/main":
    #!/bin/sh
    set -eu
    if ! git rev-parse --verify --quiet {{quote(base + "^{commit}")}} > /dev/null; then
      echo "registry: base {{base}} is not a commit (no remote yet? run `just check main`)" >&2
      exit 1
    fi
    old=$(mktemp)
    trap 'rm -f "$old"' EXIT
    if git show {{quote(base + ":registry.yaml")}} > "$old" 2> /dev/null; then
      python3 scripts/check_registry.py --base "$old"
    else
      echo "registry: WARNING base check not run, no registry.yaml on {{base}}"
      python3 scripts/check_registry.py
    fi

# Unit tests of the check script
test:
    python3 -m unittest discover -s scripts

# Secrets in the whole git history
secrets:
    gitleaks git --redact --verbose --no-banner .

# L1, run by the pre-push hook
check base="origin/main": lint (registry base) test secrets
