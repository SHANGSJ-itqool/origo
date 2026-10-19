# Origo Architecture

> Status: draft (v0.1). Marked sections are design intent; some land after v0.1.

## 1. Design philosophy

Origo is an **AI-native, minimal Linux distribution**, not a new kernel. The intelligence lives in the system layer: it routes between on-device capabilities, local models, cloud models, and third-party agents, while keeping the user in control of irreversible actions.

## 2. Layers

```
+-------------------------------------------------------------+
| Interaction layer                                           |
|   Agent-first surface (text, later voice, multimodal)      |
|   Classic desktop (Xfce/Wayland) as fallback               |
+-------------------------------------------------------------+
| Skill layer (MCP)                                           |
|   terminal | files | browser | settings | office | mail ... |
+-------------------------------------------------------------+
| Agent core                                                  |
|   intent | planner | memory | safety/confirmation | audit   |
+-------------------------------------------------------------+
| AI runtime                                                  |
|   local model (llama.cpp / Ollama) + local-cloud routing    |
+-------------------------------------------------------------+
| System services                                             |
|   systemd, NetworkManager, PipeWire, Calamares (installer)  |
+-------------------------------------------------------------+
| Linux kernel (upstream)                                     |
+-------------------------------------------------------------+
| Hardware: x86, ARM, domestic CPUs, low-spec devices         |
+-------------------------------------------------------------+
```

## 3. Components

### 3.1 Agent core
- **Intent & planner**: parse the user's goal into a plan; iterate with tool calls.
- **Memory**: persistent, cross-session, stored locally; the user can view/clear it.
- **Safety policy**: classify actions; require confirmation for destructive/irreversible ones.
- **Audit log**: every tool call and its result are recorded.

### 3.2 AI runtime & routing
- Local model first (privacy, latency, offline).
- Escalate to a cloud model when the task is too large, or to a third-party agent when a capability is not on-device.
- Routing decisions consider capability, latency, cost, and network state.

### 3.3 Skills (MCP)
Each skill is a capability with a typed description, a handler, and a risk level. Initial set: terminal, files, browser, system settings, application launch. Later: office, mail, calendar, package management.

### 3.4 Desktop & compatibility
A minimal desktop remains available for users who want direct control and for apps the agent cannot wrap. The agent is the default; the desktop is a fallback, not the center.

## 4. Updates & system integrity (post-v0.1)

- Investigate image-based / transactional updates (e.g. ostree-style) with rollback, so agent and system updates cannot brick a machine.
- Reproducible, signed builds; mirror-aware packaging for regions with limited connectivity.

## 5. Security model

- Least privilege for skills; the agent requests only the capabilities it needs.
- Human confirmation gates for high-risk actions; no autonomous spending or sending.
- Local data stays local unless the user enables cloud; private data is redacted where possible.

## 6. Hardware & regional support

- Run on old/low-spec x86 PCs and ARM boards; support domestic Chinese CPUs where feasible.
- Package mirrors for offline/intranet environments; small model sizes for low-end storage.

## 7. What we explicitly do NOT do

- Rewrite the kernel for its own sake.
- Force a cloud account or constant connectivity.
- Let the agent take irreversible actions without consent.
- Treat the user as a product or harvest their data.
