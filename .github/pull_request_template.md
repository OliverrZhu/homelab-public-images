## What changed

<!-- One-line summary: e.g. "Bump diffusers to commit abc1234" -->

## Checklist

### If bumping a dependency (diffusers / torch / CUDA base)
- [ ] `DIFFUSERS_REF` updated to a pinned commit SHA (not `main`)
- [ ] `docker build` ran locally and `/opt/skylab/runtime_smoke.py` (build step) passed
- [ ] Verified no secrets in the image: `docker history --no-trunc <image> | grep -iE 'token|key|secret|password'`
- [ ] Build log / smoke-check output pasted below

### All PRs
- [ ] `hadolint` passes (or inline `# hadolint ignore` added with justification)
- [ ] No new `detect-secrets` findings (or baseline updated with explanation)
- [ ] Trivy scan result reviewed (SARIF visible in Security tab after merge)

## Smoke-check output

```
# paste: docker build ... output (last few lines), or: docker run ... python /opt/skylab/runtime_smoke.py
```
