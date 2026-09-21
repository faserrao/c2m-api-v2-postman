#!/usr/bin/env python3
"""
generate_artifacts_index.py — Generate reports/artifacts-index.md.

Produces a Markdown table (Report Name | Link | Description) covering every
artifact committed to the c2m-api-v2-postman-artifacts repo by CI.  Links are
constructed from the GitHub org name so they work for both the click2mail
(corporate) and faserrao (personal) contexts.

Usage:
    python scripts/active/generate_artifacts_index.py --org click2mail
    python scripts/active/generate_artifacts_index.py --org faserrao

The --org value is passed automatically by the Makefile / CI using
${{ github.repository_owner }}.
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import yaml as _yaml
except ImportError:
    _yaml = None


# J12: Module-level constant so artifact repo name is a single change point.
# Must match ARTIFACTS_REPO_NAME in the Makefile / CI (passed as --artifacts-repo).
_DEFAULT_ARTIFACTS_REPO = "c2m-api-v2-postman-artifacts"

# J5: Must match API_TITLE in the Makefile and _DEFAULT_API_TITLE in
# ebnf_to_openapi_dynamic_v3.py and generate_dd_table.py.
_DEFAULT_API_TITLE = "C2M API v2"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _repo_url(org: str, path: str, artifacts_repo: str = _DEFAULT_ARTIFACTS_REPO) -> str:
    """GitHub blob URL for a file in the artifacts repo."""
    return f"https://github.com/{org}/{artifacts_repo}/blob/main/{path}"


def _repo_tree_url(org: str, path: str, artifacts_repo: str = _DEFAULT_ARTIFACTS_REPO) -> str:
    """GitHub tree URL for a directory in the artifacts repo."""
    return f"https://github.com/{org}/{artifacts_repo}/tree/main/{path}"


def _pages_url(org: str, path: str, artifacts_repo: str = _DEFAULT_ARTIFACTS_REPO) -> str:
    """GitHub Pages URL (artifacts repo, docs/ served at root)."""
    return f"https://{org}.github.io/{artifacts_repo}/{path}"


def _link(label: str, url: str) -> str:
    return f"[{label}]({url})"


def _latest_glob(pattern: str, reports_dir: Path) -> str | None:
    """Return the filename (not full path) of the lexicographically last match."""
    matches = sorted(reports_dir.glob(pattern))
    return matches[-1].name if matches else None


def _md_table(rows: list[tuple[str, str, str]]) -> str:
    lines = [
        "| Report Name | Link | Description |",
        "|---|---|---|",
    ]
    for name, link, desc in rows:
        lines.append(f"| {name} | {link} | {desc} |")
    return "\n".join(lines)


def _section(title: str, rows: list[tuple[str, str, str]], readme_url: str | None = None) -> str:
    heading = f"## {title}"
    if readme_url:
        heading += f" &nbsp;·&nbsp; {_link('README', readme_url)}"
    return f"{heading}\n\n{_md_table(rows)}\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

_DEFAULT_SDK_LANGS = [
    ("Python",     "python",     "Python client library generated from the OpenAPI spec via OpenAPI Generator."),
    ("JavaScript", "javascript", "JavaScript client library for browser and Node.js environments."),
    ("TypeScript", "typescript", "TypeScript client library with full type definitions."),
    ("Java",       "java",       "Java client library generated from the OpenAPI spec."),
    ("Go",         "go",         "Go client library generated from the OpenAPI spec."),
    ("Ruby",       "ruby",       "Ruby gem generated from the OpenAPI spec."),
    ("PHP",        "php",        "PHP client library generated from the OpenAPI spec."),
    ("C#",         "csharp",     "C# / .NET client library generated from the OpenAPI spec."),
    ("Swift",      "swift",      "Swift client library for iOS and macOS applications."),
    ("Kotlin",     "kotlin",     "Kotlin client library generated from the OpenAPI spec."),
    ("Rust",       "rust",       "Rust client library generated from the OpenAPI spec."),
]


def _load_sdk_langs(sdk_langs_path: Optional[str]) -> list:
    """Load SDK language list from config/sdk-languages.yaml.  Falls back to
    _DEFAULT_SDK_LANGS when the path is None, yaml is unavailable, or the file
    cannot be read — so CI never fails silently due to a missing file.
    """
    if sdk_langs_path and _yaml is not None:
        try:
            with open(sdk_langs_path) as f:
                data = _yaml.safe_load(f)
            langs = (data or {}).get('languages', [])
            if langs:
                return [(e['label'], e['slug'], e['description']) for e in langs]
        except Exception as exc:
            import sys
            print(f"⚠️  Could not load sdk-languages.yaml '{sdk_langs_path}': {exc} — using built-in list", file=sys.stderr)
    return _DEFAULT_SDK_LANGS


def generate(org: str, reports_dir: Path, output: Path,
             artifacts_repo: str = _DEFAULT_ARTIFACTS_REPO,
             api_name: str = "c2mapiv2",
             linked_collection_name: str = "C2M API Linked Collection",
             sdk_langs_path: Optional[str] = None) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Local URL helpers with artifacts_repo baked in
    def _url(path: str) -> str:
        return _repo_url(org, path, artifacts_repo)

    def _tree(path: str) -> str:
        return _repo_tree_url(org, path, artifacts_repo)

    def _pages(path: str) -> str:
        return _pages_url(org, path, artifacts_repo)

    # --- latest timestamped reports (glob in reports_dir) -------------------
    latest_newman_html = _latest_glob("newman-*.html", reports_dir)
    latest_validation_md = _latest_glob("validation-*.md", reports_dir)

    # --- README URLs for directory-level READMEs ----------------------------
    docs_readme    = _url("docs/README.md")
    reports_readme = _url("reports/README.md")
    # openapi/ and postman/collections/ have no README — None omits the link

    # --- Documentation (GitHub Pages) ---------------------------------------
    doc_rows = [
        (
            "API Reference — Redoc",
            _link("Open", _pages("index.html")),
            "Interactive API documentation rendered with Redoc — browse endpoints, schemas, and examples.",
        ),
        (
            "API Reference — Swagger UI",
            _link("Open", _pages("swagger.html")),
            "Interactive API documentation rendered with Swagger UI — supports try-it-out requests.",
        ),
        (
            "API Reference — Stoplight Elements",
            _link("Open", _pages("elements.html")),
            "Interactive API documentation rendered with Stoplight Elements.",
        ),
    ]

    # Shorthand for building artifact paths from the API name prefix.
    # api_name is set by --api-name (Makefile: $(C2MAPIV2_POSTMAN_API_NAME_KC)).
    n = api_name

    # --- OpenAPI Specifications ---------------------------------------------
    spec_rows = [
        (
            "Final Spec",
            _link("Download", _url(f"openapi/{n}-openapi-spec-final.yaml")),
            "Production-ready OpenAPI 3.0 specification generated from the EBNF data dictionary.",
        ),
        (
            "Final Spec — With Examples",
            _link("Download", _url(f"openapi/{n}-openapi-spec-final-with-examples.yaml")),
            "Final spec augmented with curated request/response examples for each endpoint.",
        ),
        (
            "Final Spec — With Multi-Examples",
            _link("Download", _url(f"openapi/{n}-openapi-spec-final-with-multi-examples.yaml")),
            "Final spec with multiple named examples per endpoint, used by Postman mock servers.",
        ),
        (
            "Final Spec — Fixed oneOf",
            _link("Download", _url(f"openapi/{n}-openapi-spec-final-fixed-oneOf.yaml")),
            "Final spec with oneOf discriminators corrected for stricter validators and code generators.",
        ),
        (
            "Base Spec",
            _link("Download", _url(f"openapi/{n}-openapi-spec-base.yaml")),
            "Unprocessed OpenAPI spec generated directly from the EBNF before example injection.",
        ),
        (
            "Bundled Spec",
            _link("Download", _url("openapi/bundled.yaml")),
            "Single-file version of the spec with all $refs resolved inline — useful for tools that don't support multi-file specs.",
        ),
    ]

    # --- Postman Collections ------------------------------------------------
    collection_rows = [
        (
            linked_collection_name,
            _link("Download", _url(f"postman/collections/{n}-linked-collection-flat.json")),
            "Primary API collection with all endpoints linked to the live OpenAPI spec for schema validation.",
        ),
        (
            "Test Collection",
            _link("Download", _url(f"postman/collections/{n}-test-collection-flat.json")),
            "Newman-compatible test collection with pre-request auth scripts and response assertions (C2mApiV2TestCollection).",
        ),
        (
            "Getting Started — With Examples",
            _link("Download", _url(f"postman/collections/{n}-getting-started-with-examples-collection.json")),
            "Getting Started collection populated with concrete example request bodies for hands-on exploration.",
        ),
        (
            "Getting Started — Linked",
            _link("Download", _url(f"postman/collections/{n}-getting-started-linked-collection.json")),
            "Getting Started collection linked to the live spec for real-time schema validation.",
        ),
        (
            "Getting Started — Test",
            _link("Download", _url(f"postman/collections/{n}-getting-started-test-collection.json")),
            "Getting Started collection with Newman test assertions for automated verification.",
        ),
        (
            "Real World Use Cases",
            _link("Download", _url(f"postman/collections/{n}-real-world-use-cases-collection.json")),
            "Collection demonstrating realistic end-to-end request sequences across multiple endpoints.",
        ),
    ]

    # --- SDKs — no top-level sdks/README.md; each language has its own ------
    _SDK_LANGS = _load_sdk_langs(sdk_langs_path)
    sdk_rows = [
        (
            f"SDK — {label}",
            _link("Browse", _tree(f"sdks/{slug}"))
            + " &nbsp;·&nbsp; "
            + _link("README", _url(f"sdks/{slug}/README.md")),
            desc,
        )
        for label, slug, desc in _SDK_LANGS
    ]

    # --- Data Dictionary Reports --------------------------------------------
    dd_rows = [
        (
            "Data Dictionary — Component Reference (Markdown)",
            _link("View", _url("reports/data-dictionary-table.md")),
            "Every EBNF component and its elements with field types, required flags, and natural-language descriptions.",
        ),
        (
            "Data Dictionary — Component Reference (CSV)",
            _link("Download", _url("reports/data-dictionary-table.csv")),
            "CSV export of the component reference table for use in spreadsheets and data tools.",
        ),
        (
            "Data Dictionary — Endpoints Expanded (Markdown)",
            _link("View", _url("reports/data-dictionary-endpoints-expanded.md")),
            "Each API endpoint recursively expanded to every primitive leaf field with dot-path notation and descriptions.",
        ),
        (
            "Data Dictionary — Endpoints Expanded (CSV)",
            _link("Download", _url("reports/data-dictionary-endpoints-expanded.csv")),
            "CSV export of the endpoint expanded table for use in spreadsheets and data tools.",
        ),
    ]

    # --- CI Quality Reports -------------------------------------------------
    ci_rows: list[tuple[str, str, str]] = [
        (
            "Conformance Gate",
            _link("View", _url("reports/conformance-gate.md")),
            "Postman collection conformance results — validates every request body against the generated OpenAPI spec.",
        ),
        (
            "Golden Test Suite",
            _link("View", _url("reports/golden-tests.txt")),
            "Validator and resolver unit test results — positive/negative controls and synthetic fault injection.",
        ),
    ]

    if latest_newman_html:
        ci_rows.append((
            "Newman Test Run (latest)",
            _link("View", _url(f"reports/{latest_newman_html}")),
            "Most recent Newman end-to-end test run against the live API — HTML report with request/response details and pass/fail counts.",
        ))
    else:
        ci_rows.append((
            "Newman Test Run (latest)",
            "—",
            "Not yet generated — run `make run-newman-tests` to produce this report.",
        ))

    if latest_validation_md:
        ci_rows.append((
            "Collection Validation Report (latest)",
            _link("View", _url(f"reports/{latest_validation_md}")),
            "Most recent per-endpoint conformance validation showing any fields that don't match the spec.",
        ))
    else:
        ci_rows.append((
            "Collection Validation Report (latest)",
            "—",
            "Not yet generated.",
        ))

    # --- Assemble -----------------------------------------------------------
    lines = [
        f"# {_DEFAULT_API_TITLE} — Artifacts Index",
        "",
        f"_Generated: {now}_",
        "",
        "All artifacts are produced by the CI pipeline and committed to this repository on every successful build.",
        "",
        _section("API Documentation",    doc_rows,        readme_url=docs_readme),
        _section("OpenAPI Specifications", spec_rows,      readme_url=None),
        _section("Postman Collections",   collection_rows, readme_url=None),
        _section("SDKs",                  sdk_rows,        readme_url=None),
        _section("Data Dictionary Reports", dd_rows,       readme_url=reports_readme),
        _section("CI Quality Reports",    ci_rows,         readme_url=reports_readme),
    ]

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✅ {output}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--org",
        default="click2mail",
        help="GitHub organisation / owner (default: click2mail)",
    )
    parser.add_argument(
        "--reports-dir",
        default="reports",
        help="Directory to glob for timestamped reports (default: reports)",
    )
    parser.add_argument(
        "--output",
        default="reports/artifacts-index.md",
        help="Output path (default: reports/artifacts-index.md)",
    )
    parser.add_argument(
        "--artifacts-repo",
        default=_DEFAULT_ARTIFACTS_REPO,
        help="Name of the GitHub artifacts repository (default: c2m-api-v2-postman-artifacts)",
    )
    parser.add_argument(
        "--api-name",
        default="c2mapiv2",
        help="API name prefix used in artifact filenames (Makefile: C2MAPIV2_POSTMAN_API_NAME_KC). "
             "Default: c2mapiv2",
    )
    parser.add_argument(
        "--linked-collection-name",
        default="C2M API Linked Collection",
        help="Display name for the linked collection row in the index table "
             "(Makefile: POSTMAN_LINKED_COLLECTION_NAME). Default: 'C2M API Linked Collection'",
    )
    parser.add_argument(
        "--sdk-langs",
        default=None,
        help="Path to config/sdk-languages.yaml (single source of truth for SDK language list). "
             "Falls back to the built-in list when omitted.",
    )
    args = parser.parse_args()

    generate(
        org=args.org,
        reports_dir=Path(args.reports_dir),
        output=Path(args.output),
        artifacts_repo=args.artifacts_repo,
        api_name=args.api_name,
        linked_collection_name=args.linked_collection_name,
        sdk_langs_path=args.sdk_langs,
    )


if __name__ == "__main__":
    main()
