# Datasheets (downloaded 2026-10-13) and spec cross-check
| file | part(s) | source URL |
|---|---|---|
| tbm2g_manual.pdf (+ .txt) | Kollmorgen TBM2G-06008, -06013, -07613, -08508 frameless motors (§9.3–9.6) | https://shop.oxni.ch/files/v240708160007/Kollmorgen/TBM/MN%20TBM2G%20RevB%20En.pdf |
| hd_csf_csg_catalog.pdf | Harmonic Drive CSG-17-100, CSG-25-100 (rating table, Table 8 dims, weight) | https://www.harmonicdrive.net/_hd/content/documents/csf-csg.pdf |
| rollvis_rv_tables.pdf | Rollvis RV12x4 / RV12x5 / RV12x6 planetary roller screws (p.24 loads/efficiency, p.25 nut dims) | https://rollvis.com/wp-content/uploads/2024/05/Product-Tables-Rollvis-RV-Planetary-Roller-Screw-EN.pdf |
| elmo_gold_twitter_install_guide.pdf | Elmo Gold Twitter R70/100, R50/100 (MAN-G-TWI v2.011, Table 3) | https://www.e-motionsupply.com/v/ELMO/Servo%20Drive/Gold%20Whistle/MAN-G-TWIIG_s.pdf |
| molicel_p45b.pdf | Molicel INR-21700-P45B cell (v1.4) | https://www.molicel.com/wp-content/uploads/INR21700P45B_1.4_Product-Data-Sheet-of-INR-21700-P45B-80109.pdf |
| iko_crb_catalog.pdf | IKO CRBH 6013 A output bearing | https://www.ikont.eu/files/Documents/Catalogues/CAT-57151UKv3_IKO_CRB.pdf |

## Cross-check vs values used in size.py (v3/analysis/parts.py + tbm2g.json)
| item | used | datasheet | action |
|---|---|---|---|
| TBM2G-06008/06013/07613/08508 Tc130, Tp, Kt hot, Rm, mass, Rth | as tbm2g.json | identical (script check against §9 pages) | none |
| TBM2G-07613 Km, winding C | 2.01 N·m/√W | p.284 prints 2.01 but lb-in/√W column 1.78 = 0.201 N·m/√W (typo in manual) | corrected to 0.201 in size.py (not used by selection, D winding chosen) |
| TBM2G Nmax | 8000 rpm | 8000 rpm | 95 % margin rule added (R-005) |
| CSG axial length (GEAR_LEN) | 17: 32, 25: 42 [EST] | Table 8 B: 17: 32.5, 25: 37.0 | corrected; feeds housing length/CAD |
| CSG-17 component weight | 0.15 [EST] | 0.15 kg | confirmed, [EST] tag removed |
| RV12x4 Ca / C0a / η | 17.2 / 27.2 kN / 0.89 | 17.2 / 27.2 / 0.89 direct | confirmed |
| RV12x5 | 18.1 / 27.3 / 0.89 | 18.1 / 27.3 / 0.89 | confirmed |
| RV12x6 | — | 18.4 / 26.5 / 0.88 | added as candidate |
| RV12 nut D1 / L1 | 26 / 36 [EST mapping] | D1 26, flange D4 46, L1 36 (p.25) | confirmed, [EST] removed |
| Rollvis max speed | — | **not published in the tables** | open: request d0·n limit from Rollvis (knee nut 7565 rpm) |
| Gold Twitter R70/100 Ic | 49.5 A rms, 95 V, 22.2 g | 70 A amplitude / 49.5 A rms, 95 V max; peak "2 × Ic" is stated only for non-R models; Table 3 (R types) lists no peak | keep peak = Ic (no peak credit) — confirmed conservative |
| P45B | 16.2 Wh, 70 g, 45 A | 16.2 Wh typ / 15.5 Wh min, 70 g max, 45 A cont, **max charge 13.5 A**, DC IR 15 mΩ | charge limit + IR now used in regen_sim.py; note min capacity 15.5 Wh → 1550 Wh pack minimum |

## Prices found (2026-10-13)
| part | price | source |
|---|---|---|
| Molicel P45B | €3.50/cell (1–9 999), $4.50–7.49 retail → pack cells ≈ €350 | https://cellpow.eu/product/molicel-inr21700-p45b/ ; https://liionwholesale.com/products/molicel-npe-inr-21700-p45b-50a-4500mah-flat-top-21700-battery-authorized-distributor |
| Elmo G-TWIR70/100SES | $1 737 (reseller, used); ~¥6 500 (CN listing, ≈ $0.9k) | https://spwindustrial.com/1pcs-g-twir70-100ses/ (search result; CN listing URL not captured) |
| TBM2G, CSG component sets, RV12, AksIM-2 | no public price found | remain [EST] |
