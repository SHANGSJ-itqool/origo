# Origo / 元启 OS

**An AI-native, minimal, fully open-source operating system. The AI is the interface; apps are just capabilities.**

Origo (Latin for *origin, beginning*) is a Linux-based operating system built around one belief: **computers and mobile devices exist to make us more efficient — we should not have to juggle dozens of apps to get things done.** You state a goal; a system-level agent plans the steps and calls whatever capability is needed — on the device when possible, from the network when not.

中文：元启（Origo，拉丁语"起源、本原"）是一款 AI 原生、极简、完全开源的操作系统。我们的信念是：设备是为了让人更高效，而不是让人在几十个 App 之间疲于奔命。你只需表达目标，系统级智能体负责规划并调用所需能力——端侧能做的直接做，端侧没有的从网络调用。

---

## Why Origo

Today's "AI" is mostly an app you open, or a feature bolted onto an old OS. Meanwhile users hop between apps, re-enter the same data, and tap through screens a machine could handle. Origo flips the model:

- **Intent is the interface** — no hunting for the right icon; say or type what you want.
- **Agents, not apps** — the agent orchestrates files, terminal, browser, settings and services; apps become optional "capability providers".
- **Local-first, cloud-capable** — a small model runs on-device for privacy, speed and offline use; heavy reasoning or missing services are routed to the cloud or third-party agents.
- **Safe by design** — destructive or irreversible actions (deleting files, spending money, sending messages) require explicit confirmation; every action is auditable.
- **Minimal and inclusive** — runs on old PCs and low-spec hardware, not just flagship machines.

## How it works (layered)

```
Interaction   Agent-first surface (voice / text); classic desktop as a fallback
Skills        MCP skills: terminal, files, browser, settings, office, mail...
Agent core    intent understanding, planning, persistent memory, safety, audit
AI runtime    local model (llama.cpp / Ollama) + local-to-cloud routing
System        Linux userspace services (systemd, NetworkManager, PipeWire...)
Kernel        Linux kernel (upstream, reused — never rewritten for ego)
Hardware      x86 PCs, ARM, domestic (Chinese) CPUs, low-spec devices
```

See [`docs/architecture.md`](docs/architecture.md) for the full design.

## Project status

**v0.1 — early prototype.** A bootable, installable image with a minimal desktop, a local model runtime and the Origo agent shell. Expect rough edges. The goal of v0.1 is *proof, not polish*.

## Quick start

### Try the live image / install
1. Download the latest ISO from [Releases](../../releases).
2. Flash it to a USB stick (e.g. `dd if=origo-*.iso of=/dev/sdX status=progress`, or use Rufus/balenaEtcher).
3. Boot from USB — choose **Live** to try, or **Install** (Calamares).

### Run the agent from source (Linux)
```bash
cd agent
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
origo-agent
```

## Roadmap (summary)

- **v0.1** bootable installable ISO, local model, agent shell with core skills
- **v0.2** ~10 high-frequency tasks work end-to-end; voice input; release cadence
- **v0.3** governance + first external contributors; skill/agent marketplace basics
- **v0.4–v1.0** reference cases; stable API; long-term support; immutable updates
- **Future** dual track: community edition (forever open) + enterprise edition (updates, trusted supply chain, private deployment, compliance)

Full roadmap: [`docs/roadmap.md`](docs/roadmap.md).

## Contributing

Origo is open to everyone regardless of background, degree or title — open source judges code, reliability and how you treat users. Read [`CONTRIBUTING.md`](CONTRIBUTING.md); all contributions use the [DCO](DCO.txt) (Signed-off-by). Code of conduct: [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md); governance: [`GOVERNANCE.md`](GOVERNANCE.md).

## License

- Origo agent and project code: **Apache License 2.0** ([LICENSE](LICENSE)).
- Components inherited from Linux distributions remain under their own licenses (notably GPL); we follow upstream terms and contribute patches back.
- Bundled model weights use permissive licenses (e.g. Apache-2.0-family models). Check each model's license.

## 中文说明

元启 Origo 是 AI 原生、极简、完全开源的操作系统：意图即界面，智能体取代 App 的堆砌；端侧小模型优先、云端按需调用；危险操作强制确认、全程可审计；系统轻量，旧电脑也能跑。项目当前为 v0.1 原型阶段，欢迎所有开发者参与，不看学历，只看代码与诚意。详细文档见 [`docs/`](docs/)。
