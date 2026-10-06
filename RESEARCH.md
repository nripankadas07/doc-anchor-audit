# Research and project brief

Observed: 2026-10-06T06:17:32.707146+00:00 UTC, exact query `link checker`, sorted by stars descending.
[Search receipt](https://api.github.com/search/repositories?q=link%20checker&sort=stars&order=desc&per_page=10). Only the first ten results were inspected;
this is not an exhaustive worldwide ranking. lycheeverse/lychee is the highest-star
relevant comparable found in this query. Comparables can serve broader/different workflows.

| Repository | Observed stars | Repository pushed UTC | License metadata |
|---|---:|---|---|
| [lycheeverse/lychee](https://github.com/lycheeverse/lychee) | 3980 | 2026-10-05T12:44:56Z | Apache-2.0 |
| [raviqqe/muffet](https://github.com/raviqqe/muffet) | 2614 | 2026-10-05T16:11:12Z | MIT |
| [tcort/markdown-link-check](https://github.com/tcort/markdown-link-check) | 718 | 2026-07-28T10:58:30Z | ISC |

Pushed timestamps are evidence of repository activity, not proof of response/support quality.
Commit observations for the original research are in [machine-readable evidence](research.json).
Latest PR activity can be dependency automation rather than substantive maintenance.

## User, need and smallest useful capability

Documentation maintainers reviewing repository-local Markdown links before merge. A heading rename or duplicate heading can break fragments even when the target file exists. Checks local Markdown files and heading fragments offline, with source lines and explicit coverage warnings.

Read lychee fragment-generation code, markdown-link-check index.js, docs and current issues/PRs. markdown-link-check issue #593 reports parenthesized-heading false negatives; our fixture covers that shape. A successful fixture proves our behavior only, not that current competitors still fail.

## Fair feature comparison

Lychee already handles local links and heading fragments, with a richer renderer and broad async link checking. Muffet crawls websites. markdown-link-check checks Markdown links. This tool prioritizes a small inspectable standard-library implementation and explicit source diagnostics; no claim of feature superiority.

Our install path is a source clone plus Python pip install, with no runtime third-party
dependencies. Alternatives have their documented Go/Node/Python/Rust, hosted platform or
calendar-server workflows; their setup was reviewed in current documentation, not timed.
Our example and failure checks are runnable. Our supported input surface and support are
smaller; mature alternatives have broader documentation, integrations and maintenance history.
License metadata is reported, not legal compatibility advice; no code was reused.

No equivalent cross-tool workload was measured. No speed, reliability or global ranking
superiority is claimed. Synthetic fixtures prove only our documented behavior. Negative
results and unsupported configurations are in [validation](VALIDATION.md).

## Distinctness and discovery

Compared all five candidate briefs with 138 existing README/description briefs.
Existing trace/report/diff tools do not make these five one product: their users, accepted
input contracts and working algorithms differ. The archive-preflight idea was rejected
because it overlapped the existing wheel/path safety tools. Markdown/documentation topics and duplicate/parenthesized heading examples.

Acceptance criteria: Check cross-file and percent-encoded fragments, duplicate suffixes, parentheses and precomposed Unicode; ignore code; resolve references once; distinguish missing files/anchors/references, external links and root escapes; report unsupported scope.
