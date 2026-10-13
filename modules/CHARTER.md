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
