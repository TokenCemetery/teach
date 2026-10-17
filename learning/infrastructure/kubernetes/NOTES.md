# Kubernetes Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- No interview took place for #158. The mission and arc come from the issue text, which asked for Kubernetes from the user's side up to operating it and a judgment stage, so nothing about the learner's background is known beyond what the constraints assume.

## On the arc

The whole arc was written upfront in one change, not one lesson per interactive session, and `learning-records/` is empty. Nothing here has been calibrated against a demonstrated answer, so every practice item's difficulty is a guess.

## Open threads

- The first interactive session should calibrate before teaching forward: take a practice item from lesson 5 or 13 and check whether the level is right.
- The sibling track `infrastructure/ci-cd` (#159) does not exist yet. When it lands, replace the issue link in `## Out of scope` with a link to its glossary or a reference sheet.
- Version-sensitive features move between releases: sidecar containers, in-place pod resize, Gateway API resources, kube-proxy modes. Recheck lessons 4, 10, 15 and 27 against the cited docs before relying on them.
