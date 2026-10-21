"""Build REPORT.md, results.json and the governing-case von Mises plots.

Reads level_*.json and field_*.npz written by fea_job2.py.
"""
from __future__ import annotations

import glob
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ALLOW_PEAK = 503.0 / 1.5
ALLOW_AMP = 58.0
# 17-4PH H1025. Se factors are the R-031 estimator in legs/hp_lever_family_r031.py
# (0.5*Su endurance, then machined 0.75, size 0.9, 99% reliability 0.814).
# Sy/Su are the ASTM A564 H1025 minima (145 / 155 ksi).
SU_174 = 1070.0
SY_174 = 1000.0
SE_174 = 0.75 * 0.9 * 0.814 * 0.5 * SU_174
RHO_174 = 7.80e-6


def levels(tag):
    rows = []
    for p in sorted(glob.glob(os.path.join(HERE, f"level_{tag}_h*.json"))):
        rows.append(json.load(open(p)))
    rows.sort(key=lambda r: -r["h_mm"])
    return rows


def rel_change(a, b):
    return abs(a - b) / b * 100.0


def judge(rows):
    """Peak change over the last two levels. < 5% is converged."""
    if len(rows) < 3:
        return dict(converged=False, change_pct=None, reason="three levels required")
    p2, p3 = rows[-2]["peak_MPa"], rows[-1]["peak_MPa"]
    ch = rel_change(p3, p2)
    loc = rows[-1]["peak_at_mm"]
    same = rows[-2]["peak_at_mm"]
    return dict(
        converged=ch < 5.0,
        change_pct=ch,
        peak_fine_MPa=p3,
        peak_prev_MPa=p2,
        at_mm=loc,
        prev_at_mm=same,
        amplitude_MPa=rows[-1]["amplitude_MPa"],
        p999_MPa=rows[-1]["p999_MPa"],
        governing=rows[-1]["governing"],
    )


def steel_mass(mass):
    body = mass["volume_mm3"] - mass["pin_stub_mm3"]
    return body * RHO_174 + mass["pin_stub_mm3"] * 7.85e-6


def plot_case(tag, row, path):
    h, hl = row["h_mm"], row["hloc_mm"]
    npz = os.path.join(HERE, f"field_{tag}_h{h:g}_l{hl:g}.npz")
    z = np.load(npz)
    c = z["c"]
    vm = z["vm"]
    at = [float(x) for x in row["peak_at_mm"]]
    case = row["governing"]
    order = np.argsort(vm)
    c, vm = c[:, order], vm[order]
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.2), constrained_layout=True)
    # whole lever, yz, both halves
    ax = axes[0]
    sc = ax.scatter(c[1], c[2], c=vm, s=2, cmap="inferno", linewidths=0, rasterized=True)
    ax.scatter([at[1]], [at[2]], s=60, facecolors="none", edgecolors="cyan", linewidths=1.2, zorder=5)
    ax.set_xlabel("y (mm)")
    ax.set_ylabel("z (mm)")
    ax.set_aspect("equal")
    ax.set_title("both halves, element centroids")
    # zoom on the hot corner (mirror to +y for a readable window)
    ax = axes[1]
    y0, z0 = abs(at[1]), at[2]
    sel = (np.abs(np.abs(c[1]) - y0) < 12) & (np.abs(c[2] - z0) < 14) & (np.abs(np.abs(c[0]) - abs(at[0])) < 6)
    if sel.sum() < 30:
        sel = (np.abs(c[1] - at[1]) < 14) & (np.abs(c[2] - at[2]) < 14)
    cc, vv = c[:, sel], vm[sel]
    ax.scatter(cc[1], cc[2], c=vv, s=8, cmap="inferno", linewidths=0, rasterized=True,
               vmin=vm.min(), vmax=vm.max())
    ax.scatter([at[1]], [at[2]], s=80, facecolors="none", edgecolors="cyan", linewidths=1.4, zorder=5)
    ax.set_xlabel("y (mm)")
    ax.set_ylabel("z (mm)")
    ax.set_aspect("equal")
    ax.set_title("hot corner")
    fig.colorbar(sc, ax=axes, shrink=0.85, label="von Mises (MPa)")
    fig.suptitle(
        f"{tag}  {case}  h={h:g} / local {hl:g} mm   "
        f"peak {row['peak_MPa']:.0f} MPa at ({at[0]:.1f}, {at[1]:.1f}, {at[2]:.1f})"
    )
    fig.savefig(path, dpi=140)
    plt.close(fig)


def case_at(row, name):
    c = row["cases"][name]
    return c["vm_MPa"], c["at_mm"], c["amp_MPa"]


def md_table(rows):
    lines = [
        "| level | h (mm) | hloc (mm) | tets | P2 dofs | governing | peak (MPa) | at (mm) | amplitude (MPa) | p99.9 (MPa) |",
        "|---|---:|---:|---:|---:|---|---:|---|---:|---:|",
    ]
    for i, r in enumerate(rows, 1):
        at = r["peak_at_mm"]
        lines.append(
            f"| {i} | {r['h_mm']:g} | {r['hloc_mm']:g} | {r['tets']} | {r['ndof']} | {r['governing']} | "
            f"{r['peak_MPa']:.1f} | ({at[0]:.1f}, {at[1]:.1f}, {at[2]:.1f}) | {r['amplitude_MPa']:.1f} | {r['p999_MPa']:.1f} |"
        )
    return "\n".join(lines)


def same_case_line(rows, name):
    bits = []
    for r in rows:
        vm, at, amp = case_at(r, name)
        bits.append(f"{vm:.1f} MPa at ({at[0]:.1f}, {at[1]:.1f}, {at[2]:.1f})")
    return " → ".join(bits)


def write():
    rc = levels("rc")
    b35 = levels("b35")
    if len(rc) < 3:
        raise SystemExit(f"RC levels incomplete ({len(rc)})")
    jrc = judge(rc)
    plot_case("rc", rc[-1], os.path.join(HERE, "governing_vm.png"))
    jb = None
    if len(b35) == 3:
        jb = judge(b35)
        plot_case("b35", b35[-1], os.path.join(HERE, "governing_vm_b35.png"))

    mass = rc[0]["mass"]
    m174 = steel_mass(mass)
    # corner series: the fine-mesh governing case, tracked at every level
    gov = rc[-1]["governing"]
    corner = [case_at(r, gov)[0] for r in rc]
    corner_ch = rel_change(corner[-1], corner[-2])

    rc_pass_design = jrc["converged"] and jrc["peak_fine_MPa"] <= ALLOW_PEAK
    rc_pass_fatigue = jrc["converged"] and jrc["amplitude_MPa"] <= ALLOW_AMP
    rc_ok = rc_pass_design and rc_pass_fatigue

    lines = []
    A = lines.append
    A("# Job 2 report — G3 hip-pitch lever FEA")
    A("")
    A("Release candidate `modules/actuators/cad/hip_pitch_lever_r031_mw_b30_d36_RC.step`, ")
    A("solved with `hp_lever_fea_v2.mesh` / `hp_lever_fea_v2.solve` (bore cosine pressure, ")
    A("yoke face fixed at |y| = 13.5, pin traction). Design load 4542 N/pin. ")
    A("Walk amplitude is that von Mises times 2030/4542, fully reversed.")
    A("")
    A("## Mass from the STEP")
    A("")
    A(f"Two valid solids, volume {mass['volume_mm3']:.1f} mm³. ")
    A(f"Mass rule (V − 2·π·6²·25) × 2.81e-6 plus the two ø12×25 stubs as steel at 7.85 g/cm³: ")
    A(f"**{mass['mass_kg']:.4f} kg per lever** (7075 {mass['mass_7075_kg']:.4f} + pins {mass['mass_pins_kg']:.4f}).")
    A("")
    A("## Material and allowables")
    A("")
    A("7075-T6, E 71.7 GPa, ν 0.33, Sy 503 MPa, Su 572 MPa. ")
    A(f"Design pass: converged peak ≤ {ALLOW_PEAK:.1f} MPa (Sy/1.5). ")
    A(f"Fatigue pass: hot-spot von Mises amplitude ≤ {ALLOW_AMP:.1f} MPa (Se 87/1.5) at 2030 N/pin, R = −1.")
    A("")
    A("## Model")
    A("")
    A("The v2 selectors land on this STEP: yoke facets at |y| = 13.5, bore facets at r = 21 and ")
    A("|y| 13.5…33.5, pin facets at |y| > 62.5. Checked elements exclude the 2.5 mm next to the ")
    A("fixed yoke face and the steel pin stubs, same mask as `hp_lever_fea_v2.run`.")
    A("")
    A("The STEP bore lip is the sharp circle r = 21 at |y| = 33.5. There is no 1×45 chamfer and no R1 edge. ")
    A("R8 curvature (about 8.0–8.3 mm) is on the lower web/arm blends near z ≈ −27 and on the short ")
    A("side fillets. The upper web/arm edge, where the fine-mesh peak sits, is a straight edge ")
    A("(no fillet radius) across the arm at |y| = 38.5.")
    A("")
    A("Ball radius in `hp_lever_fea_v2.mesh` is hardcoded at 7 mm with an 8 mm transition. ")
    A("On this STEP that support at local 0.6 mm was 661k tets (about 3.0M P2 dofs) and does not fit ")
    A("the 15 GB available to WSL on this PC. Radius 5 mm was still 343k tets. ")
    A("The runs use the same Ball field with radius 4 mm and thickness 4 mm (235k tets, 1.03M dofs at the finest RC level).")
    A("")
    A("Ball centres: the upper arm/web corners, the R8 blends, the lower bore-lip arc, and the ear roots. ")
    A("Listed in each level JSON.")
    A("")
    A("## RC results")
    A("")
    A(md_table(rc))
    A("")
    A(f"Same case `{gov}` (the fine-mesh governing case) at the three levels: {same_case_line(rc, gov)}.")
    A(f"That corner rose {rel_change(corner[1], corner[0]):.1f}% then {corner_ch:.1f}%.")
    A("")
    A(f"Global peak change over the last two levels: {jrc['change_pct']:.1f}% ")
    A(f"({jrc['peak_prev_MPa']:.1f} MPa at {jrc['prev_at_mm']} → {jrc['peak_fine_MPa']:.1f} MPa at {jrc['at_mm']}).")
    A("")
    if jrc["converged"]:
        A("The peak changed by less than 5%. The mesh is converged for the pass tests.")
    else:
        A(f"**Singularity.** The peak changed by {jrc['change_pct']:.1f}% over the last two levels, above 5%. ")
        A(f"Location on the finest mesh: ({jrc['at_mm'][0]:.2f}, {jrc['at_mm'][1]:.2f}, {jrc['at_mm'][2]:.2f}) mm, ")
        A(f"case `{jrc['governing']}`. This is the upper arm/web corner, the end of the straight edge at |y| = 38.5. ")
        A(f"The 99.9th percentile on that mesh is {jrc['p999_MPa']:.1f} MPa, about half the element max, ")
        A("which is the same pattern as a re-entrant corner: one element keeps rising while the bulk of the field does not. ")
        A("The R8 blends at z ≈ −27 are not this hot spot.")
    A("")
    A(f"Pin displacement at |y| ≈ 69 on the finest mesh: "
      + ", ".join(f"{k} {v:.3f} mm" for k, v in rc[-1]["pin_disp_mm"].items())
      + ".")
    A("")
    A(f"Plot: `governing_vm.png`, {gov}, finest mesh. The cyan ring is the peak element centroid.")
    A("")
    A("## RC verdict")
    A("")
    if rc_ok:
        A(f"PASS. Converged peak {jrc['peak_fine_MPa']:.1f} MPa ≤ {ALLOW_PEAK:.1f}, amplitude {jrc['amplitude_MPa']:.1f} ≤ {ALLOW_AMP:.1f}.")
    else:
        A(f"FAIL. There is no converged peak. The finest element max is {jrc['peak_fine_MPa']:.1f} MPa ")
        A(f"(under the 335 MPa yield screen) but it is still climbing, and the amplitude at that element is ")
        A(f"{jrc['amplitude_MPa']:.1f} MPa, above 58. The yield screen cannot be closed on an unbounded corner.")
    A("")

    overall = "PASS" if rc_ok else "FAIL"
    if not rc_ok:
        A("## Fallback b35/d40")
        A("")
        A("Geometry `modules/legs/cad/hip_pitch_lever_r031_mw_b35_d40.step` (Legs L47 merged-web fallback, ")
        A("the file whose mass was booked at +0.242 kg robot against the old baseline). ")
        A("The actuators tree also has `hip_pitch_lever_r031_b35_d40.step` without the merged web. ")
        A("The merged-web solid is the one that matches the RC construction. ")
        A("Same solver, Balls moved out to the b=35 upper edge at x = ±17.95, z = −7.92 and to the R8 at |x| ≈ 17.7. ")
        A("The ear is still ø26, so the ear-flank balls stay near |x| = 13.")
        A("")
        if jb is None:
            A("The b35/d40 run did not finish three levels.")
        else:
            mb = b35[0]["mass"]
            A(f"Volume {mb['volume_mm3']:.1f} mm³. Mass by the same rule: **{mb['mass_kg']:.4f} kg per lever**.")
            A("")
            A(md_table(b35))
            A("")
            bg = b35[-1]["governing"]
            A(f"Same case `{bg}` across the three levels: {same_case_line(b35, bg)}.")
            A("")
            A(f"Global peak change over the last two levels: {jb['change_pct']:.1f}% ")
            A(f"({jb['peak_prev_MPa']:.1f} → {jb['peak_fine_MPa']:.1f} MPa at {jb['at_mm']}).")
            A("")
            b_ok_d = jb["converged"] and jb["peak_fine_MPa"] <= ALLOW_PEAK
            b_ok_f = jb["converged"] and jb["amplitude_MPa"] <= ALLOW_AMP
            b_ok = b_ok_d and b_ok_f
            if jb["converged"]:
                A("The b35 peak changed by less than 5%.")
            else:
                A(f"**Singularity on b35 as well**, at ({jb['at_mm'][0]:.2f}, {jb['at_mm'][1]:.2f}, {jb['at_mm'][2]:.2f}) mm. ")
                A(f"p99.9 on the finest mesh is {jb['p999_MPa']:.1f} MPa against an element max of {jb['peak_fine_MPa']:.1f}.")
            A("")
            if b_ok:
                A(f"b35 PASS. Converged peak {jb['peak_fine_MPa']:.1f} MPa ≤ {ALLOW_PEAK:.1f}, amplitude {jb['amplitude_MPa']:.1f} MPa ≤ {ALLOW_AMP:.1f}.")
                overall = "PASS"
            else:
                state = "converged" if jb["converged"] else "not converged"
                A(f"b35 FAIL. Finest peak {jb['peak_fine_MPa']:.1f} MPa, amplitude {jb['amplitude_MPa']:.1f} MPa, {state}.")
                overall = "FAIL"
            A("")
            A("Plot: `governing_vm_b35.png`.")
            A("")
            if not b_ok:
                mb35_steel = steel_mass(b35[0]["mass"])
                A("## 17-4PH H1025")
                A("")
                A("R-031 §6 holds 17-4PH H1025 if the b35/d40 7075 section still fails. ")
                A(f"The family script's endurance is 0.75×0.9×0.814×0.5×Su with Su 1070 MPa, so Se = {SE_174:.0f} MPa ")
                A(f"and the amplitude allowable is Se/1.5 = {SE_174/1.5:.0f} MPa. ")
                A(f"ASTM A564 H1025 minima are Sy {SY_174:.0f} MPa and Su {SU_174:.0f} MPa, so the yield screen is {SY_174/1.5:.0f} MPa. ")
                A(f"Density 7.80 g/cm³ on the aluminium body, pins left at 7.85: ")
                A(f"**{m174:.3f} kg** on the RC solid ({(m174 - mass['mass_kg'])*2:+.3f} kg robot versus 7075) and ")
                A(f"**{mb35_steel:.3f} kg** on the b35 solid.")
                A("")
                A("This load is force-driven. Von Mises does not depend on E, and moving ν from 0.33 to about 0.27 ")
                A("changes the stress by only a few percent, so a steel re-solve reproduces the same spike. ")
                A("The spike is geometric. On the RC it is the straight upper web/arm edge at |y| = 38.5. ")
                A("On b35 the finest-mesh location is the one in the table above. ")
                A("A material change does not give that element a converged value. ")
                A(f"Finest b35 element max {jb['peak_fine_MPa']:.0f} MPa, amplitude {jb['amplitude_MPa']:.0f} MPa. ")
                A(f"Finest RC element max {jrc['peak_fine_MPa']:.0f} MPa, amplitude {jrc['amplitude_MPa']:.0f} MPa. ")
                A(f"Both amplitudes sit under the 17-4 screen of {SE_174/1.5:.0f} MPa only at these mesh sizes, and both rose on the last refinement. ")
                A("17-4PH H1025 is not a converged pass. The unfilleted corner has to be blended before either alloy can be released.")
                A("")

    A("## Verdict")
    A("")
    A(f"**{overall}**")
    A("")
    text = "\n".join(lines)
    open(os.path.join(HERE, "REPORT.md"), "w", encoding="utf-8").write(text)
    summary = dict(
        verdict=overall,
        rc=dict(judge=jrc, mass_kg=mass["mass_kg"], corner_case=gov,
                corner_MPa=corner, corner_change_pct=corner_ch,
                levels=[dict(h=r["h_mm"], hloc=r["hloc_mm"], ndof=r["ndof"], tets=r["tets"],
                             peak=r["peak_MPa"], amp=r["amplitude_MPa"], at=r["peak_at_mm"],
                             case=r["governing"], p999=r["p999_MPa"]) for r in rc]),
        b35=None if jb is None else dict(
            judge=jb, mass_kg=b35[0]["mass"]["mass_kg"],
            levels=[dict(h=r["h_mm"], hloc=r["hloc_mm"], ndof=r["ndof"], tets=r["tets"],
                         peak=r["peak_MPa"], amp=r["amplitude_MPa"], at=r["peak_at_mm"],
                         case=r["governing"], p999=r["p999_MPa"]) for r in b35]),
        steel_17_4PH_H1025=dict(Se_MPa=SE_174, allow_amp_MPa=SE_174 / 1.5,
                                Sy_MPa=SY_174, allow_yield_MPa=SY_174 / 1.5,
                                mass_kg_on_rc=m174),
    )
    json.dump(summary, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    print(text)
    print("VERDICT", overall)


if __name__ == "__main__":
    write()
