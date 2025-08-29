#!/usr/bin/env bash
set -euo pipefail

F=Makefile
TS=$(date +%Y%m%d-%H%M%S)
cp -i "$F" "$F.bak.$TS"

# choose sed (gsed if present)
if command -v gsed >/dev/null 2>&1; then SED=gsed; else SED=sed; fi

# 1) Fix the typo INSTAALL_PYTHON_MODULES -> INSTALL_PYTHON_MODULES
$SED -E -i '' 's/\bINSTAALL_PYTHON_MODULES\b/INSTALL_PYTHON_MODULES/g' "$F"

# 2) Replace POSTMAN_WORKSPACE_PARAM with POSTMAN_Q_ID/POSTMAN_Q
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

# 3) Update call sites to use $(POSTMAN_Q) and fix misspelling
perl -0777 -pe '
  s/\?workspace=\$\((POSTMAN_WS)\)/\$(POSTMAN_Q)/g;
  s/POSTMAN_WORKSAPCE_PARAM/POSTMAN_Q/g;
' -i "$F"

# 4) Add a venv target if missing
if ! grep -qE '^\s*\.PHONY:\s*venv\b' "$F"; then
  cat >> "$F" <<'BLOCK'
# --- tooling bootstrap ---
.PHONY: venv
venv:
	@test -x "$(VENV_PIP)" || { echo "🐍 Creating venv at $(VENV_DIR)"; $(PYTHON3) -m venv "$(VENV_DIR)"; }
	@"$(VENV_PIP)" install -U pip setuptools wheel
	@"$(VENV_PIP)" -q $(INSTALL_PYTHON_MODULES)
BLOCK
fi

# 5) Ensure generate-openapi-spec-from-dd runs venv before using VENV_PIP/PYTHON
awk '
  BEGIN{inrule=0; inserted=0}
  /^\s*\.PHONY:\s*generate-openapi-spec-from-dd\b/ {print; next}
  /^generate-openapi-spec-from-dd\s*:/ { inrule=1; print; next }
  inrule && /^\t\$\((VENV_PIP|VENV_PYTHON)\)\b/ && !inserted {
    print "\t$(MAKE) venv"
    inserted=1
  }
  inrule && !/^\t/ && NF { inrule=0 }
  { print }
' "$F" > "$F.new" && mv "$F.new" "$F"

# 6) Fix indentation on postman-workspace-debug (needs a TAB recipe line)
perl -0777 -pe '
  s/\npostman-workspace-debug:\h*\n(?!\t)/\npostman-workspace-debug:\n\t/g;
' -i "$F"

echo "✅ Applied fixes. Backup at $F.bak.$TS"
