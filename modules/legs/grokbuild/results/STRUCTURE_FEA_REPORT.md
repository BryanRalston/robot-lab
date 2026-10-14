# Structure FEA report

Job 3 of 3. Material 7075-T6. Loads at 66.5 kg. Solver is scikit-fem 12 on P2 tetrahedra, C3D27 hexahedra, and Q4 plates, units mm / N / MPa. Eight threads. CPU only. Every stress below is from a solve in `modules/legs/grokbuild/results/`. The M2 catalog was not changed.

## Acceptance

The r5 M2 line for both legs is 4.822 kg (`modules/legs/results/r5/structure_r5.json`, `total_both_kg` 4.82231676641112). The 0.04 kg bolt and bumper estimate is outside that line. The cap is 4.85 kg. This study did not add catalog mass, so the line stays at 4.822 kg.

Yield safety factor is Sy / von Mises, with Sy = 503 MPa. Pulse Goodman treats the reported stress as 0 to peak: sa = sm = σ/2, SF = 1 / (sa/159 + sm/572). Fully reversed Goodman at 0.52× is SF = 159 / (0.52 × σ) on the full-load stress. The walk load case that is already scaled by 0.52 is not run through that formula again.

| Check | Result |
| --- | --- |
| M2 line ≤ 4.85 kg | 4.822 kg. Holds. |
| Fall SF ≥ 2 on a converged section stress | Fork, knee tongue, both tubes in bending, tongue fall, and foot heel pass. Foot toe and clevis fail on the element maximum. Both of those maxima grew when the mesh was refined. |
| Goodman ≥ 1.5 | Clamp arm root is 1.472 on the fully reversed 0.52× check. Several corner maxima fail. Section stresses away from those corners pass. |
| Added mass where a check fails | Measured only for the lateral tube dent. Not measured for the clevis corner, the foot flange edge, the tongue neck corner, or the clamp root. |

## Material and loads

E = 71700 MPa, ν = 0.33, Sy = 503 MPa, Su = 572 MPa, Se = 159 MPa at 5×10^8 cycles, ρ = 2.81×10⁻⁶ kg/mm³. Shaft steel in the press-fit slice is E = 210000 MPa, ν = 0.30. DP490 in the bond model is E = 2500 MPa, ν = 0.40, thickness 0.10 mm.

W = 652.365 N. 3 body-weights = 1957.1 N. Fall = 3914.19 N. The r3 ground-reaction figure 1039.8 N was not rescaled. Knee screw 7267.4 N. Hip screw 9084.3 N. One screw body force 4542 N. Carry moment 241.5 N·m at a 73 mm instep arm, so the carry screw is 3308.2 N. The 1.5× moment used as a second foot case is 314 N·m.

## Solver checks

`verify_solver.json`, status ok.

- P2 cantilever, 439 tets, 3012 dofs. Tip 0.5557 mm against the beam value 0.5579 mm (0.40%). Bending-stress band 40.9 MPa against 48 MPa (15% low). Tip face area 100 mm².
- Lamé quarter tube, 4095 tets. Bore von Mises median 167.0 MPa against the plane-stress value 179.4 MPa (6.9% low). Hand hoop 141.7 MPa.

`fea_tubes.json` cantilever gate, C3D27, intorder 4, 64 elements, 2475 dofs. Tip −0.5553 mm against the bending target 0.5579 mm plus shear, error 1.26%. End area 100.0 mm². Converged in 159 iterations.

`plate_buckling.json`. Thin plate 100×100×1, nx = 32, reduced shear: k = 3.9692, σ_cr = 26.267 MPa against k = 4 at 26.471 MPa. Biaxial ratio 0.9933. Foot bay 28×28×3.5 mm, nx = 24, full 2×2 shear, 625 nodes: simply supported σ_cr = 3537.2 MPa (k = 3.421), clamped σ_cr = 7912.4 MPa. The bay yields at 503 MPa before it buckles.

## Foot

Half model, uy = 0 on y = 0. Closed box 240×100×18 mm, skins 3.5 mm, four 4 mm webs, 6 mm pad under the sensor, instep tower x = 58 to 88 mm with its top at z = 50 mm. Steel flange OD 60 / ID 22, z = 18 to 26 mm, and six Ø5 shanks on a 46 mm bolt circle (three in the half model). The flange top is the support. Aluminum mass 0.8703 kg, the same as the M2 foot.

Fine mesh h = 2 mm: 99722 tets (80617 aluminum, 19105 steel), 27479 nodes, 530553 dofs. Coarse mesh h = 8 mm: 5972 tets, 36060 dofs. The half-model clip goes to z = 55 mm so the instep top is in the mesh. An earlier clip at z = 30 mm deleted that face.

Patch areas at h = 2 mm: toe 758.4 mm², heel 759.5 mm², toe corner 301.7 mm², instep top 1364.4 mm².

| Case | vm max MPa | SF | 2 mm off MPa | SF | p99.9 MPa | SF | p99 MPa | location mm | u mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fall toe | 520.0 | 0.967 | 443.8 | 1.133 | 200.6 | 2.508 | 132.7 | 28.67, 10.58, 17.54 | 2.128 |
| Fall heel | 114.4 | 4.398 | 111.4 | 4.516 | 54.9 | 9.157 | 33.7 | −27.86, 12.58, 17.40 | 0.070 |
| Fall toe corner | 519.8 | 0.968 | 443.5 | 1.134 | 200.6 | 2.507 | 132.7 | same as fall toe | 2.120 |
| 3 BW toe | 260.0 | 1.935 | 221.9 | 2.267 | 100.3 | 5.015 | 66.4 | same as fall toe | 1.064 |
| 3 BW heel | 57.2 | 8.797 | 55.7 | 9.031 | 27.5 | 18.32 | 16.9 | same as fall heel | 0.035 |
| Carry 241.5 N·m | 70.9 | 7.097 | 64.6 | 7.791 | 39.0 | 12.88 | 25.9 | 88.17, 44.03, 17.55 | 0.409 |
| Need 314 N·m | 92.2 | 5.459 | 83.9 | 5.992 | 50.8 | 9.909 | 33.7 | same | 0.531 |

The fall-toe maximum is at radius 30.6 mm, on the aluminum top skin, 0.5 mm outside the steel flange (radius 30 mm). At h = 8 mm the same case peaked at 252.6 MPa, safety factor 1.991, at 33.67, 1.08, 17.25 mm (radius 33.7 mm). The maximum rose as the mesh got finer. The 2 mm sample from that hottest element is still on the flange edge, so it stays high. This is the steel-to-aluminum edge, and it was not given a fillet. No added mass was solved for it.

The 99th percentile of the fall-toe aluminum is 132.7 MPa, yield safety factor 3.79. Pulse Goodman on that value is 1.87. Fully reversed 0.52× Goodman on that value is 2.30. Pulse Goodman on the 520 MPa maximum is 0.48.

Top-skin membrane on the fall-toe case, elements with z between 16 and 18.2 mm, x between 50 and 150 mm, and more than 6 mm off the web at y = 16: 4815 elements, mean σ_xx = −47.13 MPa, 95th percentile −20.04 MPa, mean σ_zz = −0.19 MPa. Bay buckling stress is 3537 MPa simply supported. The ratio of that critical stress to the mean membrane compression is 75. The skin reaches yield before the bay buckles.

Sole contact is a rigid flat ground, penalty 2×10⁵ N/mm³ on corner nodes only, each with one third of its triangle area. The ground approach is scaled to the half-model fall load of 1957.1 N. The reaction matched that force.

| Patch | Mean pressure MPa | Peak pressure MPa | Nodes still in contact | Nodes released | CoP x mm | Approach mm |
| --- | --- | --- | --- | --- | --- | --- |
| Toe, h = 2 | 2.581 | 432.2 | 14 | 257 | 164.3 | 1.719 |
| Heel, h = 2 | 2.577 | 177.9 | 29 | 244 | −44.7 | 0.034 |
| Toe, h = 8 | 2.689 | 177.0 | 4 | 25 | 162.1 | 1.610 |
| Heel, h = 8 | 2.771 | 58.7 | 6 | 21 | −44.0 | 0.032 |

The mean pressure is the total force divided by the patch area. The peak rose from h = 8 to h = 2, and the center of pressure sits on the inner edge of each patch. That peak is a line of contact at the patch boundary. It is not a converged sole pressure. The contact stress field still peaks at the flange edge (494 MPa on the toe, safety factor 1.02).

Heel fall passes yield safety factor 2 on the maximum. Carry and the 314 N·m case pass on the maximum.

## Thigh clamp

h = 1.5 mm, fillets of 1.5 mm on the arm-root lines and arcs. A 2 mm fillet failed to build. Half model. 56145 tets, 13066 nodes, 269805 dofs. Mass 0.2375 kg against the catalog 0.2372 kg. The r5 retention target of 0.295 kg adds the sleeve, pins, and glue, which are in the bond section below. Eye traction is uniform on the whole Ø12 cylinder. The half-model eye area is 903.1 mm² and the net force is 4542 N.

| Case | vm max MPa | SF | 2 mm off | SF | p99.9 | SF | u mm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4542 N | 207.75 | 2.421 | 205.87 | 2.443 | 122.47 | 4.107 | 0.105 |
| 0.52× of that load | 108.03 | 4.656 | 107.05 | 4.699 | 63.68 | 7.899 | 0.054 |

The peak is at −5.83, 31.62, 14.69 mm, the arm root, and the value 2 mm away is almost the same. It is a real root stress. Yield safety factor on 4542 N passes. Fully reversed Goodman at 0.52× of the 207.75 MPa peak is 1.472. Two millimetres away it is 1.485. The p99.9 value gives 2.497. The allowable stress for a fully reversed factor of 1.5 is 203.8 MPa. The root is 4 MPa over that. A thicker arm was not re-solved, so the added mass is not known. The printed Goodman number on the already-scaled 0.52× case (4.80 at p99.9) applies the 0.52 factor a second time and is not the fatigue result.

## Hip ring

Ø96 × 25 mm, bore Ø80, neck to the femur fix. Mass 0.2254 kg. This ring is not in the r5 mass rollup. h = 2 mm: 45420 tets, 10840 nodes, 221148 dofs, all aluminum. The bore cosine integrates to the requested force. On the physical case the moment came back as 191124 N·mm against 192000 N·mm.

| Case | Force N | Moment N·mm | vm max | SF | 2 mm off | SF | p99.9 | SF | location mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10.06 kN + 192 N·m | 10062.5 | 191124 | 911.7 | 0.552 | 777.3 | 0.647 | 499.3 | 1.007 | 19.56, −11.67, −43.39 |
| 12.4 kN radial | 12400 | residual −1080 | 251.9 | 1.997 | 230.1 | 2.186 | 179.6 | 2.800 | −19.37, −9.59, −43.41 |
| 12.4 kN + 192 N·m stacked | 12400 | 190920 | 870.5 | 0.578 | 731.0 | 0.688 | 489.2 | 1.028 | same neck corner |

The unit couple on this bore has a moment of 6.405 N·mm per 1 N, so the scale that makes 192 N·m is about 30000 N on each half. One half of that traction is tension. A 13 mm bearing width cannot carry 192 N·m as compression. The 912 MPa field is a bonded model with a tensile bore traction. It is not a contact stress.

The compressive case is 12.4 kN. Its maximum is 251.9 MPa at the neck junction, yield safety factor 1.997. Two millimetres away, 230.1 MPa, safety factor 2.186. p99.9 is 179.6 MPa, safety factor 2.80. Pulse Goodman on the maximum is 0.988, on p99.9 is 1.385. Fully reversed 0.52× Goodman is 1.214 on the maximum, 1.329 two millimetres away, and 1.702 on p99.9. A fillet at that junction was not re-solved.

## Femur and tibia tubes

C3D27, one element through the 1.2 mm wall, 36 around, 16 along an 80 mm stub, 576 elements, 21384 dofs. Mid-side nodes on the inner and outer surfaces are projected back onto the cylinders. The end load is the beam stress F/A + M y / I. The integrated axial force matched the applied force to well under 1%.

Femur Ø50 × 1.2, area 183.97 mm², I = 54798 mm⁴, moment arm 120 mm.

| Case | Band max MPa | p99 MPa | Hand MPa | SF | End force N |
| --- | --- | --- | --- | --- | --- |
| 3 BW | 110.05 | 109.88 | 117.78 | 4.571 | −1957.1 |
| Fall | 220.10 | 219.76 | 235.57 | 2.285 | −3914.2 |

Tibia Ø45 × 1.2, area 165.12 mm², I = 39627 mm⁴, moment arm 100 mm.

| Case | Band max MPa | p99 MPa | Hand MPa | SF | End force N |
| --- | --- | --- | --- | --- | --- |
| 3 BW | 115.40 | 115.25 | 122.98 | 4.359 | −1957.1 |
| Fall | 230.80 | 230.50 | 245.95 | 2.179 | −3914.2 |

Both fall bending cases pass safety factor 2. The finite-element band sits 6 to 7% under the beam formula.

Axial eigenvalue, one end fixed and one end free, L = 80 mm. Femur σ_cr = 738.7 MPa against the simply supported classical value 2156.7 MPa (ratio 0.343). Tibia σ_cr = 805.4 MPa against 2402.9 MPa (ratio 0.335). Both eigenvalues are above Sy, so the wall yields before this mode. Against the fall bending stress the ratios are 738.7/220.1 = 3.36 and 805.4/230.8 = 3.49.

Dent model: both ends fixed, a lateral patch at mid-span, |z − L/2| < 8 mm and |θ| < 18°, force equal to the leg load in +x. Patch area 349.1 mm² on the femur and 314.2 mm² on the tibia.

| Wall | Femur vm MPa | Femur SF | Femur mass one kg | Added both kg | Tibia vm MPa | Tibia SF | Tibia mass one kg | Added both kg |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.2 mm | 469.29 | 1.072 | 0.1543 | 0 | 487.78 | 1.031 | 0.1485 | 0 |
| 1.6 mm | 318.39 | 1.580 | 0.2041 | 0.0995 | 327.22 | 1.537 | 0.1962 | 0.0954 |
| 2.0 mm | 231.36 | 2.174 | 0.2530 | 0.1973 | 236.05 | 2.131 | 0.2430 | 0.1890 |
| 2.4 mm | 176.03 | 2.858 | 0.3011 | 0.2935 | 178.69 | 2.815 | 0.2889 | 0.2807 |

Safety factor 2 is von Mises of 251.5 MPa. Linear interpolation of the solved stresses between 1.6 and 2.0 mm, with the outside diameter held, puts that stress at about 1.91 mm on the femur and 1.93 mm on the tibia. The added mass is about 0.175 kg for both femurs and 0.173 kg for both tibias, together about 0.35 kg. Adding that to the M2 line would make it about 5.17 kg, over 4.85 kg. The bending fall at 1.2 mm already passes. This dent is the full fall force applied sideways on an 80 mm stub. It was not written into the catalog.

## Clevis, knee tongue, fork

Real pins. Half models where the part is symmetric. The pin traction is uniform on the exposed cylinder, and the net force is the value passed to the loader.

Knee tongue, h = 2 mm, 49549 tets, 227322 dofs, aluminum mass 0.2340 kg (catalog 0.2332). Pin area 799.7 mm².

| Case | vm max | SF | p99.9 | SF | p99 | pulse max | rev 0.52 max | u mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fall | 31.35 | 16.05 | 21.23 | 23.70 | 11.87 | 7.94 | 9.76 | 0.009 |
| 3 BW + knee screw | 73.87 | 6.81 | 50.03 | 10.06 | 27.98 | 3.37 | 4.14 | 0.020 |
| GRF + knee screw | 66.53 | 7.56 | 45.05 | 11.17 | 25.20 | 3.74 | 4.60 | 0.018 |

The knee tongue passes the fall yield check and both Goodman forms on the maximum.

Fork, h = 2 mm, 18630 tets, 95124 dofs, aluminum mass 0.1581 kg (catalog 0.1580). No collar. Pin area about 677 mm². A coarser h = 4 mm fall peak was 65 MPa.

| Case | vm max | SF | p99.9 | SF | p99 | pulse max | rev 0.52 max | u mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fall | 89.11 | 5.65 | 57.16 | 8.80 | 26.39 | 2.79 | 3.43 | 0.019 |
| 3 BW | 44.56 | 11.29 | 28.58 | 17.60 | 13.19 | 5.59 | 6.86 | 0.010 |
| Carry screw | 98.99 | 5.08 | 63.49 | 7.92 | 29.31 | 2.51 | 3.09 | 0.021 |

The fork passes. The peak is on the inner wall at −1.69, 18.51, 16.71 mm. It rose from 65 MPa at h = 4 mm to 89 MPa at h = 2 mm and is still far under yield. The hand fall net-tension figure was 93.8 MPa.

Clevis, aluminum mass 0.2345 kg (catalog 0.2346). The ears are two solids until the Ø16 pin joins them. Pin area about 1044 mm² at h = 2 mm and 1051 mm² at h = 4 mm.

h = 2 mm: 30041 tets, 150270 dofs.

| Case | vm max | SF | p99.9 | SF | p99 | p50 | pulse max | pulse p99.9 | u mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fall | 339.0 | 1.484 | 152.3 | 3.304 | 56.5 | 3.42 | 0.734 | 1.634 | 0.104 |
| 3 BW + knee screw | 798.9 | 0.630 | 358.8 | 1.402 | 133.3 | 8.06 | 0.311 | 0.693 | 0.246 |
| GRF + knee screw | 719.5 | 0.699 | 323.1 | 1.557 | 120.0 | 7.26 | 0.346 | 0.770 | 0.221 |

h = 4 mm: 5484 tets, 30981 dofs.

| Case | vm max | SF | 2 mm off | SF | p99.9 | SF | p99 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Fall | 233.2 | 2.157 | 228.7 | 2.199 | 197.0 | 2.553 | 75.7 |
| 3 BW + knee screw | 549.5 | 0.915 | 539.0 | 0.933 | 464.3 | 1.083 | 178.4 |
| GRF + knee screw | 494.9 | 1.016 | 485.4 | 1.036 | 418.1 | 1.203 | 160.7 |

Every maximum is at the cheek/bridge corner, near 3, 21, 40 mm. From h = 4 to h = 2 the fall maximum rose from 233 to 339 MPa and the screw maximum rose from 550 to 799 MPa, while p99 fell (fall 76 to 57 MPa, screw 178 to 133 MPa). The peak is growing as the corner is resolved. The h = 4 “2 mm” sample is still that corner, because the elements are 4 mm. The h = 2 file was written before the 2 mm sample existed, so a distance off the fine-mesh corner was not stored. A fillet was not re-solved. The added mass that would bring this corner under a safety factor of 2 was not measured.

On the fine mesh the fall p99 is 56.5 MPa (yield safety factor 8.9) and the screw-case p99 is 133.3 MPa (yield safety factor 3.77, pulse Goodman 1.87). Those are the stresses outside the top 1% of elements. The literal maximum does not pass.

## Femur tongue and press-fit

Tongue solid: OD 55 × 27 mm, bore Ø35, neck to the femur fix. Mass 0.1837 kg against the hand mass 0.183 kg. h = 2 mm: 36012 tets, 172527 dofs. The bore pressure is applied only for |y| < 13.3 mm so the flat hub ends are not loaded. The mechanical resultant was 10062.5 N and 192049 N·mm against 10062.5 N and 192000 N·mm. Couple scale on the design moment is 14143 N per unit-couple half. The one-screw fault uses 5520.5 N and 505398 N·mm (192 N·m plus 4542 N × 69 mm). Its couple scale is 37227.

| Case | vm max | SF | 2 mm off | SF | p99.9 | SF | location mm | u mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 60 MPa pressure | 195.6 | 2.572 | 195.5 | 2.573 | 191.4 | 2.628 | 16.52, 4.23, 7.02 | 0.071 |
| 49.2 MPa, +60 K | 160.4 | 3.137 | 160.3 | 3.138 | 157.0 | 3.204 | same bore point | 0.058 |
| 10.06 kN + 192 N·m | 262.0 | 1.920 | 261.8 | 1.921 | 183.9 | 2.735 | −9.38, −12.67, −25.40 | 0.253 |
| Fault, 505 N·m | 842.4 | 0.597 | 814.4 | 0.618 | 479.1 | 1.050 | same neck corner | 0.668 |
| Fall | 34.46 | 14.60 | 32.66 | 15.40 | 25.73 | 19.55 | 9.30, −1.01, −25.33 | 0.010 |
| Pressure + design load | 349.3 | 1.440 | 321.3 | 1.566 | 221.6 | 2.269 | 9.42, 12.65, −25.39 | 0.253 |
| Hot pressure + design load | 324.9 | 1.548 | 301.2 | 1.670 | 193.2 | 2.603 | same | 0.252 |
| Pressure + fault | 730.6 | 0.688 | 680.3 | 0.739 | 456.1 | 1.103 | neck corner | 0.663 |
| Pressure + fall | 202.4 | 2.486 | 200.8 | 2.505 | 196.8 | 2.556 | 17.96, −2.79, −0.06 | 0.081 |

The fall passes. The design load plus the press-fit does not: 349 MPa at the hub surface where the neck face meets the cylinder, and 321 MPa two millimetres away. A filleted or thicker neck was not re-solved, so the added mass is not known.

Bore radial stress from the element field (centroids inside r = 19 mm). A negative value is tension in the bonded model.

| Case | p min MPa | p median MPa | mid-bore p median | mid-bore hoop median | Open |
| --- | --- | --- | --- | --- | --- |
| 60 MPa | +40.7 | 51.2 | 51.0 | 130.1 | no |
| Pressure + design load | −1.69 | 41.1 | 41.0 | 105.6 | yes, barely |
| Hot + design load | −10.1 | 31.8 | 31.5 | 82.4 | yes |
| Pressure + fault | −59.5 | 40.9 | 40.5 | 76.1 | yes |

Hand Lamé hoop at 60 MPa is 141.7 MPa. The mid-bore hoop median is 130 MPa. The bore elements are not only the surface, so the median sits under the applied pressure. The design-load superposition just opens the bore (minimum −1.7 MPa). The fault opens it widely. Those bonded peaks are not contact solutions.

Plane-strain press-fit slice, `fea_press.json`. Shaft r = 15 to 17.5 mm plus the radial interference, hub r = 17.5 to 27.5 mm. One bonded penalty solve. Contact pressure is −σ_rr at the hub bore. Status PRESS_PASS on the interference gate (pressure median in 50 to 70 MPa, bore hoop median in 110 to 175 MPa).

| Case | p median | p min | p max | hoop median | hoop max | open sectors | gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.0705 mm radial | 56.19 | 56.19 | 56.19 | 146.41 | 146.41 | 0 of 72 | no |
| +60 K, δ = 0.0578 mm | 45.97 | 45.97 | 45.97 | 119.79 | 119.79 | 0 | no |
| 910 N/mm needle | 58.39 | −9.31 | 74.55 | 138.34 | 159.78 | 2 | yes |
| Needle, hot | 48.18 | −19.78 | 64.35 | 111.68 | 133.32 | 2 | yes |
| 373 N/mm mean | 57.09 | 29.36 | 63.71 | 143.11 | 151.89 | 0 | no |

Hand values: pressure 60 MPa, hoop 141.7 MPa, hot pressure 49.2 MPa, hot hoop 116.2 MPa. The 910 N/mm line is the 9.1 kN needle share per 10 mm of seat. Two sectors go into tension. The recorded tangential displacement under that line is 0.00024 mm. That is the bonded stick-spring movement, with kt = 2×10⁵ N/mm³. It is not a friction return-map amplitude. The mean line load of 373 N/mm stays closed.

## Thigh clamp bond and pin holes

Axisymmetric Q4, full 2πr integration. Sleeve r = 21.8 to 23.7 mm over z = 0 to 34 mm, glue 0.10 mm on each side of the 1.2 mm tube, collar out to r = 31 mm. The tube is fixed at z = −12 mm. Unused grid nodes are fixed so they do not singularize the matrix. The model is axial and the proof load. The 2.39 kN transverse load and the 313 N·m one-screw fault are not in it.

At 8763.86 N the hand average shear is 1.641 MPa. The element-mean shear is 1.638 MPa at every mesh tried. Tube σ_z below the bond is 47.644 MPa against 8764 / 183.97 = 47.637 MPa. Mid-bond tube σ_z is 6.33 MPa. Above the bond it is about 0.3 MPa, because the load is applied on the collar top and enters the tube through the glue.

The element on the collar end rises as the axial mesh is refined. That is the bimaterial corner.

| Stations along the 34 mm bond | Corner peak MPa | z of that peak mm | Shear near 1 mm | Shear near 2 mm |
| --- | --- | --- | --- | --- |
| 14 | 7.38 | 1.31 | (same element) | (same element) |
| 28 | 9.38 | 0.63 | (element at 0.63) | 5.06 at 1.89 mm |
| 56 | 10.79 | 0.31 | 7.80 at 0.93 mm | 4.44 at 2.16 mm |
| 112 | 11.66 | 0.15 | 7.21 at 1.07 mm | 4.75 at 1.99 mm |

The comparison value is the shear about 2 mm in from the end on the finest mesh: 4.75 MPa at 8764 N. Against 11.5 MPa at 23 °C the factor is 2.42. Against 4.75 MPa at 82 °C the factor is 1.00. One millimetre in, the shear is 7.21 MPa, factors 1.59 and 0.66. The corner element itself is past 11.5 MPa on the 112-station mesh and was still rising.

Proof 13100 N, 28 stations: corner 14.02 MPa, shear near 2 mm is 7.57 MPa at z = 1.89 mm, factors 1.52 at 23 °C and 0.63 at 82 °C. Walking axial load 0.52 × 8764 N: shear near 2 mm is 2.63 MPa, factors 4.37 and 1.80.

Pin-hole coupon: 80 × 48 mm plate, Ø6 hole, 25032 triangles, plane stress. Remote stress 1 MPa, peak 2.909 MPa, Kt = 2.909. Gate 2.6 to 3.4 passed.

Bond-failed tube, walking: 0.52 × 8763.86 N on area 183.97 mm² is 24.77 MPa gross, times Kt is 72.05 MPa. Yield safety factor 6.98. Fully reversed Goodman 2.21. This is the coupon Kt times the walking membrane stress. It is not a 3D pin-hole model. Hand pin bearing at the full 8764 N is 114 MPa (safety factor 4.41). That bearing number is the hand check, not an FEA result.

Bond-intact tube at mid-bond: 6.33 MPa at 8764 N, so 3.29 MPa at the walking load, times Kt is 9.57 MPa. Fully reversed Goodman on that stress is 16.6. The hole is assumed at mid-collar. The pins were not meshed.

## Mass

FEA solid masses against the numbers used in the rollup:

| Part | FEA kg | Rollup kg |
| --- | --- | --- |
| Foot aluminum | 0.8703 | 0.8703 |
| Clamp aluminum, with 1.5 mm fillets | 0.2375 | 0.2372 catalog, 0.295 with sleeve, pins, and glue |
| Hip ring | 0.2254 | not in the r5 line |
| Clevis aluminum | 0.2345 | 0.2346 |
| Knee tongue | 0.2340 | 0.2332 |
| Fork | 0.1581 | 0.1580 |
| Femur tongue | 0.1837 | 0.183 hand |

No volume from these meshes was written back into the M2 line. The line remains 4.822 kg.

The only added-mass number this study measured is the lateral dent. Reaching safety factor 2 under that patch takes about 0.35 kg on both legs and would put the line near 5.17 kg. That thickness was not adopted. The clevis corner, the foot flange edge, the tongue neck corner, and the clamp root each miss a stated factor on a local peak, and none of those geometry changes was re-solved.
