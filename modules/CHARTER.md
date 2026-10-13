# Robot Lab module program (started 2026-10-13)
Goal: an Optimus-class humanoid that would actually work if manufactured. Baseline: v3 in /workspace/robot-lab/v3 (DESIGN, PARTS, REVISIONS, dashboard.json, cad/, analysis/), sim in sim/v3.
Coordinator: Robot Lab (9598b055). Phase 1 agents: Actuators, Legs, Arbiter.

## Rules
- Each module owns its folder in modules/<name>/: SPEC.md, checks, CAD, results.
- CONTRACTS.md is the only source of truth for interfaces and budgets: mass, peak/continuous power, envelope, mounting pattern, bus/data, torque/speed.
- No module changes another module's files or a contract on its own. It proposes the change in modules/PROPOSALS.md (who, what, why, numbers). If the affected owner disagrees, the Arbiter rules.
- Arbiter rules only against TARGETS.md (whole-robot targets, Bryan approved) and evidence (checks, datasheets, sim). Rulings logged in modules/RULINGS.md.
- Work in rounds, one agent at a time; Robot Lab sequences them. Bryan's crew rule: one job at a time crew-wide (Grok Bot releases).
- Every claim cites a datasheet/source or a check script; estimates marked [EST]. Commit to git after each step as Bryan Ralston <BryanRalston@users.noreply.github.com>; push with gh.

## Progress media (for Bryan's future process video)
After every round that changes the design, save dated images to media/progress/ named YYYY-MM-DD_<module>_<what>.png: the 3D model (assembled + exploded, same camera angles each time), key plots, and sim screenshots or short clips. Add a line to media/progress/LOG.md saying what changed. Never delete old media.

## Usage (Bryan, 2026-10-13 10:07 AM)
Conserve Grok Bot usage; other projects need it. Keep rounds tight: one focused deliverable per turn, no exploratory sprawl, no polling, reuse existing scripts. If a Grok Bot usage limit is hit, Grok Build via Grok Interface may supplement, one session at a time, only through Robot Lab and the crew one-job rule.
Update (Bryan, 10:08 AM): Grok Build may be used whenever it makes sense, not only at a limit; prefer it to save Grok Bot usage. One session at a time via Grok Interface (aa95bf5f), requested through Robot Lab.

## Standing decisions (Bryan via Grok Bot, 2026-10-13 10:12 AM)
- Agents decide for themselves when to use Grok Build for testing/training; don't ask Bryan these judgment calls. One session at a time via Grok Interface on the "bryan" PC (check it has a usable GPU first), routed through Robot Lab under the crew one-job rule. No cloud agents without Grok Bot's OK.
- Walking: push model-based walking on CPU first; GPU RL only when truly needed (via Grok Build as above).
- Spending/budget limit: noted but NOT enforced; project is theoretical for now. Keep listing real part costs for reference.
