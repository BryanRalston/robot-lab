"""Build REPORT.md, results.json and the governing-case plots from level JSON."""
from __future__ import annotations

import glob
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ALLOW_PEAK = 271.0
ALLOW_AMP = 58.0
HAND = {
    "upper_r8": dict(peak_MPa=119.0, amp_MPa=53.0, note="nominal 88/39, Kt 1.35"),
    "ear_r5": dict(amp_lo_MPa=48.0, amp_hi_MPa=64.0, note="D92 hand estimate [EST]"),
}


def load_levels(tag):
    rows = []
    for path in sorted(glob.glob(os.path.join(HERE, f"level_{tag}_h*_l*.json"))):
        rows.append(json.load(open(path)))
    rows.sort(key=lambda r: -r["h_mm"])
    return rows


def dist(a, b):
    return float(np.linalg.norm(np.asarray(a, float) - np.asarray(b, float)))


def sym_dist(a, b):
    """Closest image under the lever's ±x and ±y copies. z is not mirrored."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    best = 1e9
    for sx in (1.0, -1.0):
        for sy in (1.0, -1.0):
            bb = np.array([sx * b[0], sy * b[1], b[2]])
            best = min(best, float(np.linalg.norm(a - bb)))
    return best


def judge(rows):
    out = dict(n_levels=len(rows), complete=len(rows) >= 3)
    if len(rows) < 3:
        out.update(converged=False, singular=None, static_pass=False, fatigue_pass=False,
                   verdict="INCOMPLETE")
        return out
    fine = rows[-1]
    prev = rows[-2]
    rel = abs(fine["peak_MPa"] - prev["peak_MPa"]) / prev["peak_MPa"]
    loc_abs = dist(fine["peak_at_mm"], prev["peak_at_mm"])
    # The four ear fillets, and the four upper fillets, are copies. A governing
    # corner that swaps side between levels is the same hot spot.
    loc = sym_dist(fine["peak_at_mm"], prev["peak_at_mm"])
    ratio = fine["p999_MPa"] / fine["peak_MPa"]
    conv_peak = rel < 0.05
    conv_loc = loc <= 2.0
    conv_bulk = ratio >= 0.75
    converged = bool(conv_peak and conv_loc and conv_bulk)
    static_pass = bool(converged and fine["peak_MPa"] <= ALLOW_PEAK)
    fatigue_pass = bool(converged and fine["amplitude_MPa"] <= ALLOW_AMP)
    out.update(
        converged=converged,
        rel_change=rel,
        location_shift_mm=loc,
        location_shift_absolute_mm=loc_abs,
        p999_over_peak=ratio,
        conv_peak=conv_peak,
        conv_location=conv_loc,
        conv_bulk=conv_bulk,
        static_pass=static_pass,
        fatigue_pass=fatigue_pass,
        peak_MPa=fine["peak_MPa"],
        amplitude_MPa=fine["amplitude_MPa"],
        peak_at_mm=fine["peak_at_mm"],
        singular=None if converged else fine["peak_at_mm"],
        verdict="PASS" if static_pass and fatigue_pass else "FAIL",
    )
    return out


def plot_case(tag, row, path):
    npz = os.path.join(HERE, f"field_{tag}_h{row['h_mm']:g}_l{row['hloc_mm']:g}.npz")
    if not os.path.isfile(npz):
        return
    z = np.load(npz)
    c = z["c"]
    vm = z["vm"]
    at = [float(x) for x in row["peak_at_mm"]]
    order = np.argsort(vm)
    c, vm = c[:, order], vm[order]
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.2), constrained_layout=True)
    ax = axes[0]
    sc = ax.scatter(c[1], c[2], c=vm, s=2, cmap="inferno", linewidths=0, rasterized=True)
    ax.scatter([at[1]], [at[2]], s=60, facecolors="none", edgecolors="cyan", linewidths=1.2, zorder=5)
    ax.set_xlabel("y (mm)")
    ax.set_ylabel("z (mm)")
    ax.set_aspect("equal")
    ax.set_title("both halves, element centroids")
    ax = axes[1]
    y0, z0 = abs(at[1]), at[2]
    sel = (np.abs(np.abs(c[1]) - y0) < 12) & (np.abs(c[2] - z0) < 14) & (np.abs(np.abs(c[0]) - abs(at[0])) < 6)
    if int(sel.sum()) < 30:
        sel = (np.abs(c[1] - at[1]) < 14) & (np.abs(c[2] - at[2]) < 14)
    cc, vv = c[:, sel], vm[sel]
    ax.scatter(cc[1], cc[2], c=vv, s=8, cmap="inferno", linewidths=0, rasterized=True, vmin=float(vm.min()), vmax=float(vm.max()))
    ax.scatter([at[1]], [at[2]], s=80, facecolors="none", edgecolors="cyan", linewidths=1.4, zorder=5)
    ax.set_xlabel("y (mm)")
    ax.set_ylabel("z (mm)")
    ax.set_aspect("equal")
    ax.set_title("hot spot")
    fig.colorbar(sc, ax=axes, shrink=0.85, label="von Mises (MPa)")
    fig.suptitle(
        f"case {tag}  {row['governing']}  h={row['h_mm']:g} / local {row['hloc_mm']:g} mm   "
        f"peak {row['peak_MPa']:.0f} MPa at ({at[0]:.1f}, {at[1]:.1f}, {at[2]:.1f})"
    )
    fig.savefig(path, dpi=140)
    plt.close(fig)


def fmt_at(at):
    return f"({at[0]:.2f}, {at[1]:.2f}, {at[2]:.2f})"


def level_table(rows):
    lines = [
        "| level | h / hloc | ball r | tets | ndof | governing | peak MPa | p99.9 | p99.9/peak | location mm | amp MPa |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(rows, 1):
        lines.append(
            f"| {i} | {r['h_mm']:g} / {r['hloc_mm']:g} | {r['ball_r_mm']:g} | {r['tets']} | {r.get('ndof', '')} | "
            f"{r['governing']} | {r['peak_MPa']:.2f} | {r['p999_MPa']:.2f} | {r['p999_over_peak']:.3f} | "
            f"{fmt_at(r['peak_at_mm'])} | {r['amplitude_MPa']:.2f} |"
        )
    return "\n".join(lines)


def sample_lines(row):
    s = row.get("surface_samples") or {}
    bits = []
    n = s.get("outward_normal")
    if n:
        bits.append(f"outward normal {n}, surface gap {s.get('surface_gap_mm')} mm")
    for key, label in (("d2_mm", "2 mm"), ("d4_mm", "4 mm")):
        q = s.get(key)
        if not q:
            continue
        bits.append(
            f"{label} inward: {q['vm_MPa']:.1f} MPa (amp {q['amp_MPa']:.1f}) "
            f"at {fmt_at(q['at_mm'])}, {q['elem_dist_mm']:.2f} mm from the target"
        )
    return "; ".join(bits) if bits else "not computed"


def family_table(rows):
    lines = [
        "| level | upper R8 | ear R5 | lower R8 | bore lip |",
        "|---|---|---|---|---|",
    ]
    for i, r in enumerate(rows, 1):
        fam = r.get("families") or {}
        cells = []
        for name in ("upper_r8", "ear_r5", "lower_r8", "bore_lip"):
            q = fam.get(name)
            cells.append(f"{q['vm_MPa']:.1f} / {q['amp_MPa']:.1f}" if q else "—")
        lines.append("| " + str(i) + " | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def family_line(row):
    fam = row.get("families") or {}
    bits = []
    for name in ("upper_r8", "ear_r5", "lower_r8", "bore_lip"):
        q = fam.get(name)
        if not q:
            bits.append(f"{name}: no element inside the ball")
        else:
            bits.append(f"{name}: {q['vm_MPa']:.1f} MPa / amp {q['amp_MPa']:.1f} at {fmt_at(q['at_mm'])}")
    return "; ".join(bits)


def section(tag, title, rows, gate):
    lines = [f"## Case {tag}: {title}", ""]
    if not rows:
        lines.append("No levels finished.")
        lines.append("")
        return lines
    mass = rows[-1]["mass"]
    lines.append(
        f"Volume {mass['volume_mm3']:.1f} mm³. Mass {mass['mass_kg']:.4f} kg per lever "
        f"(7075 body {mass['mass_7075_kg']:.4f} kg, steel pins {mass['mass_pins_kg']:.4f} kg)."
    )
    lines.append("")
    lines.append(level_table(rows))
    lines.append("")
    lines.append("Family maxima inside each Ball, peak / amplitude in MPa:")
    lines.append("")
    lines.append(family_table(rows))
    lines.append("")
    fine = rows[-1]
    lines.append(f"Finest-level families (max inside the Ball radius on the governing case): {family_line(fine)}.")
    lines.append("")
    lines.append(f"Off-surface samples on the finest governing case: {sample_lines(fine)}.")
    lines.append("")
    if gate["verdict"] == "INCOMPLETE":
        lines.append(f"Gate: INCOMPLETE ({gate['n_levels']} of 3 levels). No pass, and no extrapolation.")
    else:
        lines.append(
            f"Convergence, levels 2 to 3: peak change {100 * gate['rel_change']:.2f}% "
            f"({'under 5%' if gate['conv_peak'] else '5% or more'}), "
            f"same fillet after folding ±x/±y: shift {gate['location_shift_mm']:.2f} mm "
            f"({'yes, within 2 mm' if gate['conv_location'] else 'no, more than 2 mm'}), "
            f"absolute coordinate shift {gate['location_shift_absolute_mm']:.2f} mm, "
            f"p99.9/peak {gate['p999_over_peak']:.3f} "
            f"({'at least 0.75' if gate['conv_bulk'] else 'below 0.75'})."
        )
        if gate["converged"]:
            lines.append(
                f"Converged. Static {gate['peak_MPa']:.1f} MPa vs 271 MPa: "
                f"{'PASS' if gate['static_pass'] else 'FAIL'}. "
                f"Amplitude {gate['amplitude_MPa']:.1f} MPa vs 58 MPa: "
                f"{'PASS' if gate['fatigue_pass'] else 'FAIL'}."
            )
        else:
            lines.append(
                f"Not converged. Singular at {fmt_at(gate['singular'])}. "
                f"The level-3 element max is {gate['peak_MPa']:.1f} MPa and the amplitude is "
                f"{gate['amplitude_MPa']:.1f} MPa. Those numbers are not a pass and are not extrapolated."
            )
        lines.append(f"Case verdict: **{gate['verdict']}**.")
    lines.append("")
    return lines


def _fam(row, name):
    fam = (row.get("families") or {}).get(name)
    return None if not fam else fam


def hand_text(loaded):
    lines = [
        "D92 estimate: upper R8 peak about 119 MPa and amplitude about 53 MPa (nominal 88/39, Kt 1.35). "
        "Ear R5 amplitude about 48–64 MPa. The FEA columns below are the maxima inside those Balls. "
        "A value is not a converged Kt when it is still moving, or when p99.9 is far below the element max.",
    ]
    for tag in ("a", "b"):
        rows = loaded.get(tag) or []
        if len(rows) < 2:
            lines.append(f"Case {tag}: not enough levels for a trend.")
            continue
        bits = []
        for name, label in (("upper_r8", "upper R8"), ("ear_r5", "ear R5")):
            seq = [_fam(r, name) for r in rows]
            if any(q is None for q in seq):
                continue
            trend = " → ".join(f"{q['vm_MPa']:.0f}/{q['amp_MPa']:.0f}" for q in seq)
            rel = abs(seq[-1]["vm_MPa"] - seq[-2]["vm_MPa"]) / seq[-2]["vm_MPa"]
            bits.append(f"{label} {trend} MPa (peak/amp), last step {100 * rel:.0f}%")
        lines.append(f"Case {tag}: " + "; ".join(bits) + ".")
    lines.append(
        "Where the last step is over 5%, that blend is not converged. Do not read it as beating or missing the hand estimate."
    )
    return "\n\n".join(lines)


def main():
    cases = {
        "a": "b34/d40/e26, governing geometry",
        "b": "b30/d36/e26, fillet-only comparison",
    }
    loaded = {tag: load_levels(tag) for tag in cases}
    gates = {tag: judge(rows) for tag, rows in loaded.items()}
    # Overall is the governing geometry. A missing case A cannot pass.
    overall = gates["a"]["verdict"] if loaded["a"] else "INCOMPLETE"
    if overall == "INCOMPLETE":
        overall_token = "FAIL"
    else:
        overall_token = overall

    lines = [
        "# Job 2R — G3 hip-pitch lever FEA (brief G3-R2)",
        "",
        "Solver: `hp_lever_fea_v2.mesh` / `solve` (gmsh OCC tets, Ball size fields, scikit-fem P2, pyamg CG). "
        "Same boundary-condition selectors as job 2: cosine pressure on the ø42 bore, yoke face fixed at |y| = 13.5, "
        "pin traction on the ear pins. Design load 4542 N per pin. Fully reversed amplitude is the design von Mises "
        "times 2030/4542. Linear elasticity, so that scale is exact for one load case.",
        "",
        "Material: 7075-T651 plate, thickness along x (ST), single load path. Static gate ≤ 271 MPa. "
        "Fatigue gate ≤ 58 MPa at 2030 N/pin, R = −1. E = 71.7 GPa and ν = 0.33 are the job 2 solver constants. "
        "The von Mises field is force-driven, so E cancels; ν is unchanged from job 2.",
        "",
        "Mesh: Ball radius 4 mm and thickness 4 mm, 14 centres only. Levels h/hloc = 4/1.5, 3/1.0, 2.5/0.6. "
        "A level over 300k tets would be remeshed at Ball radius 3 mm. That did not happen unless a level record says so.",
        "",
        "Ball centres, case A (case B shifts the upper and lower x with the arm width):",
        "",
        "- Upper R8, 45° point on the blend cylinder at z = −14: A (±19.34, ±40.84, −14), B (±17.34, ±40.84, −14).",
        "- Ear-root R5, brief centres: both cases (±13, ±48, −52).",
        "- Lower R8, fillet-edge midpoints: A (±17.37, ±38.50, −25.71), B (±15.09, ±38.50, −27.30).",
        "- Bore lips, arm side of the r = 21 circle: both cases (0, ±33.5, −21).",
        "",
        "Check mask is the job 2 mask: drop elements within 2.5 mm of the yoke face and the steel pin stubs. "
        "Peak is the element-maximum von Mises on the symmetric (both pins) cases.",
        "",
        "D92 hand estimate to compare, not a gate: upper R8 peak about 119 MPa and amplitude about 53 MPa; "
        "ear R5 amplitude about 48–64 MPa.",
        "",
        f"Overall verdict (case A, the b34/d40 lever): **{overall}**.",
        "",
    ]
    for tag, title in cases.items():
        lines.extend(section(tag, title, loaded[tag], gates[tag]))
    lines.extend([
        "## Hand estimate",
        "",
        hand_text(loaded),
        "",
        "## If this fails",
        "",
        "The next geometry step in G3-R2 is ear Ø26 → 28 with the R5 kept. The rod sweep has to be checked again "
        "(Ø32 was 0.5 mm). This re-run does not switch the lever to 17-4PH.",
        "",
    ])
    report = "\n".join(lines)
    open(os.path.join(HERE, "REPORT.md"), "w", newline="\n").write(report)
    payload = dict(overall=overall, overall_token=overall_token, allow_peak_MPa=ALLOW_PEAK,
                   allow_amp_MPa=ALLOW_AMP, hand=HAND, gates=gates,
                   levels={tag: [{k: r[k] for k in (
                       "h_mm", "hloc_mm", "ball_r_mm", "tets", "nodes", "ndof", "governing",
                       "peak_MPa", "p999_MPa", "p999_over_peak", "peak_at_mm", "amplitude_MPa",
                       "mass", "families", "surface_samples")} if "ndof" in r else r
                       for r in loaded[tag]] for tag in cases})
    # The comprehension above is awkward if ndof missing. Rebuild cleanly.
    slim = {}
    keys = ["h_mm", "hloc_mm", "ball_r_mm", "ball_t_mm", "tets", "nodes", "ndof", "governing",
            "peak_MPa", "p999_MPa", "p999_over_peak", "peak_at_mm", "amplitude_MPa",
            "fault_peak_MPa", "fault_at_mm", "mass", "families", "surface_samples", "facets"]
    for tag, rows in loaded.items():
        slim[tag] = [{k: r[k] for k in keys if k in r} for r in rows]
    payload["levels"] = slim
    json.dump(payload, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    for tag, rows in loaded.items():
        if not rows:
            continue
        plot_case(tag, rows[-1], os.path.join(HERE, f"governing_vm_{tag}.png"))
    print("VERDICT", overall, "TOKEN", overall_token)
    for tag, g in gates.items():
        print(tag, g["verdict"], "levels", g["n_levels"])


if __name__ == "__main__":
    main()
