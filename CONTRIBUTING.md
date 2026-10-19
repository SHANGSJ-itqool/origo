# Contributing to Origo

First off: **thank you.** Origo is built by people who believe computers should serve humans, not the other way around. Anyone can contribute — your background, degree, age or employer are irrelevant here. What matters is working code, reliability, and how you treat other people.

## Ways to contribute

- **Code** — agent core, skills, UI, ISO build, packaging, ports to new hardware.
- **Docs & translation** — fix typos, write guides, translate (English/中文 welcome).
- **Testing** — run the ISO on real hardware, file clear issues with logs.
- **Skills & agents** — add MCP skills or wrap services as agents.
- **Design** — minimal UI, boot splash, branding (see `branding/`).
- **Community** — help newcomers, answer questions, share the project.

## Ground rules

1. Read and follow the [Code of Conduct](CODE_OF_CONDUCT.md).
2. Every change must be signed with the [DCO](DCO.txt): add `Signed-off-by: Your Name <email>` to commits (`git commit -s`).
3. One logical change per pull request; keep it small and reviewable.
4. Describe **what** and **why** in the PR; include test evidence for behavior changes.
5. Match the existing style; add tests for new logic.

## Development setup

```bash
# Linux (or WSL2)
cd agent
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
origo-agent --help
```

To build the ISO, see [`iso/README.md`](iso/README.md).

## Pull request checklist

- [ ] `git commit -s` (DCO sign-off present)
- [ ] Tests pass / manual verification described
- [ ] Docs updated if behavior changed
- [ ] No secrets, large binaries, or unrelated reformatting

## Filing issues

Include: hardware/VM, image version, exact steps, expected vs actual result, and relevant logs (`journalctl`, `/var/log`). Security-sensitive reports should be posted privately to maintainers, not in public issues.

## Decision making

See [GOVERNANCE.md](GOVERNANCE.md): rough consensus, technical merit, and maintainer review. Maintainers may merge, request changes, or decline — a declined PR with a clear reason is not personal.
