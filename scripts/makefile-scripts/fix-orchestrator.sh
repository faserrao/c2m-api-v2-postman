#!/usr/bin/env bash
set -euo pipefail

f=Makefile
ts=$(date +%Y%m%d-%H%M%S)
cp -i "$f" "$f.bak.$ts"

# 1) Fix the typo in requirements installer
if command -v gsed >/dev/null 2>&1; then
  gsed -ri 's/\bINSTAALL_PYTHON_MODULES\b/INSTALL_PYTHON_MODULES/g' "$f"
else
  sed -E -i '' 's/\bINSTAALL_PYTHON_MODULES\b/INSTALL_PYTHON_MODULES/g' "$f"
fi

# 2) Introduce POSTMAN_Q_ID / POSTMAN_Q if the old single var is present
if grep -q 'POSTMAN_WORKSPACE_PARAM' "$f"; then
  if command -v gsed >/dev/null 2>&1; then
    gsed -ri 's#^POSTMAN_WORKSPACE_PARAM.*#POSTMAN_Q_ID := ?workspaceId=$(POSTMAN_WS)\nPOSTMAN_Q    := ?workspace=$(POSTMAN_WS)#' "$f"
  else
    # BSD sed (macOS)
    sed -E -i '' $'s#^POSTMAN_WORKSPACE_PARAM.*#POSTMAN_Q_ID := ?workspaceId=$(POSTMAN_WS)\nPOSTMAN_Q    := ?workspace=$(POSTMAN_WS)#' "$f"
  fi
fi

# 3) Replace usage: force mocks/collections/environments to use $(POSTMAN_Q)
if command -v gsed >/dev/null 2>&1; then
  gsed -ri 's/\?workspace=\$\(POSTMAN_WS\)/$(POSTMAN_Q)/g; s/POSTMAN_WORKSAPCE_PARAM/POSTMAN_Q/g' "$f"
else
  sed -E -i '' 's/\?workspace=\$\(POSTMAN_WS\)/$(POSTMAN_Q)/g; s/POSTMAN_WORKSAPCE_PARAM/POSTMAN_Q/g' "$f"
fi

# 4) Add a venv target if missing
if ! grep -qE '^\s*\.PHONY:\s*venv' "$f"; then
  cat >> "$f" <<'EOS'

# --- tooling bootstrap ---
.PHONY: venv
venv:
	@test -x "$(VENV_PIP)" || { echo "🐍 Creating venv at $(VENV_DIR)"; $(PYTHON3) -m venv "$(VENV_DIR)"; }
	@"$(VENV_PIP)" install -U pip setuptools wheel
	@"$(VENV_PIP)" -q $(INSTALL_PYTHON_MODULES)
EOS
fi

# 5) Ensure generate-openapi-spec-from-dd triggers venv before using pip
awk '
  BEGIN{block=0; done=0}
  {lines[NR]=$0}
  /^(|\.PHONY:\s*)generate-openapi-spec-from-dd:/ {block=1}
  block && /^\t\$\(VENV_PIP\)\b/ && !done {
    print "\t$(MAKE) venv"
    done=1
  }
  {print $0}
' "$f" > "$f.tmp" && mv "$f.tmp" "$f"

# 6) Fix indentation on postman-workspace-debug (Make needs a TAB)
if command -v gsed >/dev/null 2>&1; then
  gsed -ri 's@^postman-workspace-debug:\s*$@postman-workspace-debug:@' "$f"
  gsed -ri 's@^(postman-workspace-debug:\s*)\n[ ]+@postman-workspace-debug:\n\t@' "$f" || true
else
  # Try a gentle replacement on macOS sed
  perl -0777 -pe 's/postman-workspace-debug:\s*\n +/@FIX@/s; s/@FIX@/postman-workspace-debug:\n\t/s' -i "$f" || true
fi

echo "✅ Applied fixes. Backup at $f.bak.$ts"
