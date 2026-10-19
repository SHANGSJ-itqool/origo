# Origo Roadmap

> Living document. Dates are targets, not promises; the release *cadence* matters more than exact dates.

## v0.1 — Bootable proof (week 1)
- [x] Bootable, installable Debian-based image (live-build + Calamares)
- [x] Minimal Xfce desktop as fallback
- [x] Agent core: intent, planner, tools, memory, safety, audit
- [x] Core skills: terminal, files, browser, settings, launch app
- [x] Local-first LLM via OpenAI-compatible backend (Ollama)
- [ ] Public repo + v0.1 release notes + demo video

## v0.2 — Usable (weeks 2–4)
- [ ] ~10 high-frequency tasks work end-to-end (open apps, find files, change settings, install software, check system info, create notes, basic web lookup, timers, calendar handoff)
- [ ] Voice input (local STT where possible)
- [ ] First-run model setup (download from reachable mirrors)
- [ ] Release cadence (weekly), change log
- [ ] Community channel (chat/discussion)

## v0.3 — Community (months 2–3)
- [ ] 3–5 external contributors; clear good-first-issues
- [ ] DCO in CI; basic automated checks; packaging
- [ ] Skill/agent authoring guide and examples
- [ ] Optional Ollama + model bundled image; ARM64 image

## v0.4–v1.0 — Reference & stability (months 3–12)
- [ ] Reference cases (old-PC revival; later vertical devices)
- [ ] Stable skill/API with deprecation policy
- [ ] Image-based/transactional updates with rollback
- [ ] Signed, reproducible builds; security hardening
- [ ] Long-term support baseline; installed-base in the thousands

## Future — dual track
- Community edition: forever free and open.
- Enterprise edition: long-term updates, trusted AI supply chain, private/on-prem deployment, hardware certification, audit/compliance, support SLAs.
- Possible foundation home for trademarks and governance.

## How priorities are set
User impact > reliability > new features. Bugs that break tasks beat new skills. Every roadmap item should trace to a real user scenario.
