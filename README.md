# CASMI research observatory

Public, buildless evidence dashboard. The CASMI research source repository remains private.

Each process component has a stable component ID, a URL fragment, and a prefilled GitHub issue link. Process logs start at dashboard registration; they record observed artifact/HEAD changes, not invented executions. Published official score contrasts are not isolated causal attribution.

Serve `docs/` with a local HTTP server or GitHub Pages. `tools/sync.py` exports an allowlisted snapshot from the local CASMI workspace: official public scores, transformation IDs, diagnostic aggregate metrics, schema glossary and hashes. No spectra, model binaries, credentials, private raw logs or hidden test labels are exported. Run `python tools/sync.py --watch --publish` to observe selected sources and publish changed snapshots every minute. Requires a local checkout and existing Git authentication. Stop that process to pause publishing.

Git selectors inspect historical `VERSIONS.json` snapshots. They do not checkout the source worktree. Full code comparisons require access to the separate private source repository.

Local state is ignored. Public snapshot fields are reviewed in `tools/sync.py`; do not replace them with arbitrary logs. New experiments must be added deliberately to this allowlist. GitHub Pages publication can lag a local change. The snapshot timestamp identifies the actual exported state.

## Structured process events

Example: `python tools/log_event.py --component ML-01 --run-id encoder-run-20261123 --status started`.
Finish with `--status completed --metric dev_mrr25 --value 0.3 --baseline 0.29` only when that metric has actually been measured. Metric type explicitly preserves evaluation scope. This logger does not certify the measurement. Raw messages and free-form process output are deliberately not published. The observer watches selected evidence files; it does not automatically instrument every existing training process. Producers must call the event logger to record run lifecycles.

Components UI-01, LOG-01, GIT-01 and LIN-01 cover the observatory itself. All IDs have deep links and prefilled issues. Source components point to the private research repository; UI/logging sources point to this public repository.

## Verification

`uv run --no-project --with playwright python tests/test_dashboard.py` checks browser behavior in a separate headless Chrome. The checked score is the initial reviewed fixture; update that assertion deliberately when a new official snapshot changes it. `docs/qa.json` records the completed UI checks; it does not certify the scientific validity of the results.

The local macOS LaunchAgent `nl.ehmac.casmi-observatory` keeps the watcher running during the logged-in session. Stop with `launchctl bootout gui/$(id -u)/nl.ehmac.casmi-observatory`. Restart with `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/nl.ehmac.casmi-observatory.plist`. No credentials are stored in this project; publishing uses existing Git authentication.
