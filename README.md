# doc-anchor-audit

Checks local Markdown files and heading fragments offline, with source lines and explicit coverage warnings.

Built for documentation maintainers reviewing repository-local Markdown links before merge. A heading rename or duplicate heading can break fragments even when the target file exists.

## Quickstart

Python 3.11 or later. No runtime dependencies, service account or API key.
Clone the public source, create an isolated environment and install:

```sh
git clone https://github.com/nripankadas07/doc-anchor-audit.git
cd doc-anchor-audit
python -m venv .venv
. .venv/bin/activate
python -m pip install .
doc-anchor-audit .
```

Expected synthetic demo outcome: all local Markdown target/fragment checks pass with no coverage warnings. JSON goes to stdout.
Use `--help` for options. On Windows, activate with `.venv\Scripts\activate`.
Windows is not locally validated in this launch; remote CI covers Linux Python 3.11/3.12/3.13.

## Contract

Check cross-file and percent-encoded fragments, duplicate suffixes, parentheses and precomposed Unicode; ignore code; resolve references once; distinguish missing files/anchors/references, external links and root escapes; report unsupported scope.

Exit 0 means the supported input has no gated finding; 1 means a finding or gate failure;
2 means malformed or unsupported input/coverage. Read the JSON counts and limitations
before interpreting a zero result as comprehensive validation.

## Limitations

A documented Markdown subset, not a complete CommonMark/GFM renderer. Supports ordinary ATX/Setext headings, duplicate suffixes, precomposed Unicode, simple emphasis/code in heading text, inline/image/reference/shortcut links, fenced code and plain list/blockquote links. Nested headings/fences, HTML/MDX, ambiguous indented links, local query strings and non-Markdown fragments produce warnings and exit 2. Supports empty <a id="…"></a> or name anchors only. Nested labels and complex inline rendering are outside scope and should be checked with a full renderer; escaping/slug Unicode edge cases may differ. External links counted but never fetched. Missing local files/anchors and root escapes fail. Markdown symlinks outside root reject. Excludes .git/node_modules/venv/build/dist; 1000 files, 2 MB/file, 20 MB total.

## Verify and contribute

```sh
python -m unittest -v
python -m compileall -q doc_anchor_audit.py
python -m pip install build
python -m build
```

The tests exercise successful behavior and meaningful failure cases. See
[validation](VALIDATION.md), [research](RESEARCH.md), [contribution guidance](CONTRIBUTING.md)
and [security guidance](SECURITY.md). Open a reproducible issue with a synthetic fixture;
do not post private exports or credentials. MIT licensed; implementation is original,
with no competitor code or prose copied.
