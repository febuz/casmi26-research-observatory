# CASMI research observatory

Public, buildless evidence dashboard. The CASMI research source repository remains private.

Each process component has a stable component ID, a URL fragment, and a prefilled GitHub issue link. Process logs start at dashboard registration; they record observed artifact/HEAD changes, not invented executions. Published official score contrasts are not isolated causal attribution.

Serve `site/` with a local HTTP server or GitHub Pages. `tools/sync.py` exports an allowlisted snapshot from the local CASMI workspace: official public scores, transformation IDs, diagnostic aggregate metrics, schema glossary and hashes. No spectra, model binaries, credentials, private raw logs or hidden test labels are exported. Run `python tools/sync.py --watch --publish` to observe selected sources and publish changed snapshots every minute. Requires a local checkout and existing Git authentication. Stop that process to pause publishing.

Git selectors inspect historical `VERSIONS.json` snapshots. They do not checkout the source worktree. Full code comparisons require access to the separate private source repository.

Local state is ignored. Public snapshot fields are reviewed in `tools/sync.py`; do not replace them with arbitrary logs. New experiments must be added deliberately to this allowlist. GitHub Pages publication can lag a local change. The snapshot timestamp identifies the actual exported state.
