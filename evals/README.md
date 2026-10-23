# Evals: shadow audits

These evals measure whether the skills find real bugs and avoid false ones. The method is the **shadow audit** (from Zealynx's Krait): run a skill blind on code whose bugs are already public, then score what it reports against the published findings.

No results are recorded yet. Until runs exist under `results/`, the repo makes no precision or recall claims.

## Rules

1. **Blind input.** Audit a sanitized copy of the code at the commit *before* the fixes. Remove everything listed in the case's `sanitize` field (audit reports, known-issues lists, answer keys, test names that name the bug) and the Git history after that commit. The skill must never see the ground truth.
2. **Pinned setup.** Record the skill commit, model, profile (`quick`/`standard`/`deep`), budget, and date with every result.
3. **Same safety rules.** Runs follow the skill's own rules: read-only target, sandboxed execution, no network.
4. **Adjudicate, don't assume.** A confirmed finding that matches no ground-truth item is not automatically a false positive, because audits miss bugs too. A person reviews each one and records `true-positive-new`, `false-positive`, or `duplicate`.

## Case format

`cases/<id>.json`; see `cases/_template.json`. Each ground-truth item has a `scope` (the function, template, route, or contract that holds the root cause) and `keywords` that any correct description of the root cause would use.

Seed cases: three Circom bugs from the [zkbugs](https://github.com/zksecurity/zkbugs) dataset, with ground truth adapted from zkSecurity's `circom-auditor` benchmarks (`skills/circom-auditor/evals/`). Good next additions are public Code4rena, Sherlock, or Cantina contests with final reports (for EVM), and public audit reports with fix commits (for other stacks).

## Running one case

```bash
# 1. Prepare the blind copy (outside this repo)
git clone <repo_url> /tmp/eval/<id>-src && git -C /tmp/eval/<id>-src checkout <ref>
cp -R /tmp/eval/<id>-src/<path> /tmp/eval/<id>      # then delete the case's sanitize entries
# 2. Run the skill on /tmp/eval/<id> with the chosen profile; output goes to <out>/
# 3. Score
python3 -I evals/score.py evals/cases/<id>.json <out>/findings.json --json > evals/results/<id>-<skill-commit>-<date>.json
```

Then add the human adjudication of `unmatched_confirmed_for_adjudication`, plus the run metadata from rule 2, to the results file.

## Metrics

- `recall_confirmed`: ground-truth items matched by a `confirmed` record.
- `recall_any`: the same, also counting `needs_validation` matches.
- `wrongly_rejected`: ground-truth items that were found but then rejected in verification. These are the cases the revival review exists for.
- `precision_lower_bound`: matched confirmed records divided by all confirmed records. After adjudication, true precision = (matched + adjudicated true positives) / confirmed.

Track these per skill version, so a change to the gates or lenses shows whether it traded recall for precision.
