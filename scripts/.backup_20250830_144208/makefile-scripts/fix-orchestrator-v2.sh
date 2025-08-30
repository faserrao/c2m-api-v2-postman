#!/usr/bin/env bash
set -euo pipefail

F=Makefile
TS=$(date +%Y%m%d-%H%M%S)
cp -i "$F" "$F.bak.$TS"

# 1) Fix the typo INSTAALL_PYTHON_MODULES -> INSTALL_PYTHON_MODULES
if command -v gsed >/dev/null 2>&1; then SED=gsed; else SED=sed; fi
# in-place on macOS BSD sed needs an arg for -i
$SED -E -i'' 's/\bINSTAALL_PYTHON_MODULES\b/INSTALL_PYTHON_MODULES/g' "$F"

# 2) Replace the POSTMAN_WORKSPACE_PARAM definition with the two new vars
awk '
  BEGIN{replaced=0}
  {
    if (!replaced && $0 ~ /^POSTMAN_WORKSPACE_PARAM[[:space:]]*:=/) {
      print "POSTMAN_Q_ID := ?workspaceId=$(POSTMAN_WS)"
      print "POSTMAN_Q    := ?workspace=$(POSTMAN_WS)"
      replaced=1
      next
    }
    print
  }
' "$F" > "$F.new" && mv "$F.new" "$F"

# 3) Update call sites to use $(POSTMAN_Q) and fix the misspelling POSTMAN_WORKSAPCE_PARAM
# Use perl for reliable literal replacement without shell escaping headaches
perl -0777 -pe '
  s/\?workspace=\$\((POSTMAN_WS)\)/\$(POSTMAN_Q)/g;
  s/POSTMAN_WORKSAPCE_PARAM/POSTMAN_Q/g;
' -i "$F"

# 4) Add a venv target if it doesn’t exist
if ! grep -qE '^\s*\.PHONY:\s*venv\b' "$F"; then
  cat >> "$F" <<'EOF'

# --- tooling bootstrap ---
.PHONY: venv
venv:
	@test -x "$(VENV_PIP)" || { echo "🐍 Creating venv at $(VENV_DIR)"; $(PYTHON3) -m venv "$(VENV_DIR)"; }
	@"$(VENV_PIP)" install -U pip setuptools wheel
	@"$(VENV_PIP)" -q $(INSTALL_PYTHON_MODULES)
EOF
fi

# 5) Ensure generate-openapi-spec-from-dd runs `make venv` before using VENV_PIP
awk '
  BEGIN{inrule=0; inserted=0}
  # rule header
  /^\s*\.PHONY:\s*generate-openapi-spec-from-dd\b/ {print; next}
  /^generate-openapi-spec-from-dd\s*:/ { inrule=1; print; next }
  inrule && /^\t\$\((VENV_PIP|VENV_PYTHON)\)\b/ && !inserted {
    print "\t$(MAKE) venv"
    inserted=1
  }
  # end of recipe when next non-tab or empty line after a tabbed block
  inrule && !/^\t/ && NF { inrule=0 }
  { print }
' "$F" > "$F.new" && mv "$F.new" "$F"

# 6) Fix indentation on postman-workspace-debug (needs a TAB recipe line)
# Normalize header, then ensure a tabbed echo line follows
perl -0777 -pe '
  s/\npostman-workspace-debug:\h*\n(?!\t)/\npostman-workspace-debug:\n\t/g;
' -i "$F"

echo "✅ Applied fixes. Backup at $F.bak.$TS"

