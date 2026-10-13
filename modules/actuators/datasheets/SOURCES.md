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

## Harness (R5 A2, O16), downloaded 2026-10-13
| file | part(s) | data used | source URL |
|---|---|---|---|
| lapp_oelflex_heat180_sif.pdf | Lapp ÖLFLEX HEAT 180 SiF silicone single cores, 0.25–4 mm² | weight kg/km 5.4/9/12/15/20/32/50 for 0.25/0.5/0.75/1/1.5/2.5/4 mm²; OD; fixed bend 6×OD | https://media.distrelec.com/Web/Downloads/_t/ds/Lapp_OLFLEX_HEAT_180SIF_eng_tds.pdf |
| gore_hs_data_cables_catalog.pdf | GORE GSC-03-84820-00 Ethernet Quadrax Cat5e 26 AWG (EtherCAT 100BASE-TX) | 3.3 mm OD, 15 mm min bend, 23.0 kg/km | https://kr.gore.com/system/files/2024-08/Gore-High-Speed-Data-Cables-Catalog-US.pdf |
| igus_cfbus.pdf | igus chainflex CFBUS.040 Cat5 (flex-rated reference) | 7.0 mm, 59 kg/km | https://media.digikey.com/pdf/Data%20Sheets/Igus%20PDFs/CFBUS.pdf |
| igus_cfrobot4.pdf | igus chainflex CFROBOT4 (torsion reference) | 9–11.5 mm, 72–135 kg/km | https://media.digikey.com/pdf/Data%20Sheets/Igus%20PDFs/CFROBOT4.pdf |
| amass_catalog_xt60.pdf | Amass catalogue incl. XT60 / XT60U / AS150U | ratings | https://www.china-amass.com/public/upload/20240620/94b600a6a4c042646bc89646abc8ea85.pdf |
| amass_xt30u.pdf | Amass XT30U-M | 15 A cont, 18 AWG, 500 V | https://www.blizzcartz.com/files/Data%20Sheets/Power/Batteries%20and%20Chargers/Battery%20Connectors/XT30U-M_AMASS_Datasheet.pdf |
| amass_mr30.pdf | Amass MR30 | 15 A, 16 AWG | https://sparks.gogo.co.nz/assets/_site_/downloads/MR30_SPEC.pdf |
| amass_as150u_2025.pdf | Amass AS150U (2+4) 2025V0 | 75 A, 80 V DC rating. Note: below the 84 V bus max, see D43 | https://www.china-amass.net/uploads/97.AS150U%EF%BC%882+4%EF%BC%89-M-SPEC-2025V0.pdf |
| jst_gh.pdf | JST GH 1.25 mm | 1 A, AWG 30–26 | https://www.jst-mfg.com/product/pdf/eng/eGH.pdf |

**Connector masses are not in the Amass or JST datasheets.** Masses used:
- XT60: 7.8 g/pair (Alise Operations listing).
- XT30: 1.8 g per half, and MR30: 1.2 g/pc (AMOV Lab listing, https://amovrobotlab.com/products/amass-connector-xt90s-xt90-s-xt30u-xt60-xt90-mr30-xt60h-cables).
- JST-GH and AS150U: [EST].

## R5b (O20 flex cable, O21 connector masses), downloaded 2026-10-13
| file | part(s) | data used | source URL |
|---|---|---|---|
| belden_mrta2p26s.pdf | Belden MachFlex MRTA2P26S robotic 2 pr 26 AWG shielded | 4.2 mm OD, 25.9 kg/km, 8e6 bend cycles at 7.5D, 8e6 torsion cycles ±180°/m | https://catalog.belden.com/techdata/EN/MRTA2P26S_techdata.pdf |
| staubli_cables_catalog.pdf | Stäubli SILI-E super-flexible silicone wires (0.07 mm strands) | kg/km 4.5/8.6/12/16/22/33 for 0.25/0.5/0.75/1/1.5/2.5 mm²; OD | https://www.staubli.com/content/dam/ecs/catalogs-brochures/TM/CAB-Main-11014119-en.pdf |

Rejected for not fitting the drums (r_min 34–53 mm):
- Lapp ETHERLINE P Flex Cat.5e 2×2×AWG26: 5.6 mm, 45 kg/km, flexing bend 15 × OD = 84 mm (https://e.lapp.com/apac/p/ethernet-cable/etherline-p-flex-cat-5e-4x2xawg26-7-2170300).
- igus CFBUS.040: 7.0 mm, 59 kg/km.

Connector masses (O21):
- AS150U: 41.4 g/pair (Rotorama, https://www.rotorama.com/product/amass-as150u-1-par).
- JST-GH 4-pin: 0.5 g/pair, calculated from jst_gh.pdf dimensions.

Joint ranges: from the v3 MJCF, `sim/v3/humanoid_v3.xml` (CONTRACTS "Range of motion").
