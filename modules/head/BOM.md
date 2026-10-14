# Head/neck BOM (P-019 / R-025, A23 citation pass 2026-10-14). There's no repo-wide BOM yet.
Bus: 20S pack, 68–84 V (R1.3). Neck servos run on the brain carrier's RS485 (Gauntlet AGX301, 2× RS-232/RS-485, CTIM-00140), not EtherCAT.

| Qty | Part | Mass kg (each) | Basis | Unit price | Source |
|---|---|---|---|---|---|
| 2 | ROBOTIS Dynamixel XM430-W350-R | 0.082 | catalog | $333.39 | https://www.robotis.us/dynamixel-xm430-w350-r/ |
| 1 | Stereolabs ZED X Mini 2.2 mm (ZED-311210) | 0.150 | catalog | $549 | https://www.stereolabs.com/store/products/zed-x-mini-stereo-camera |
| 1 | 6806-2RS 30×42×7 yaw bearing | 0.026 | catalog | $9.95 | mass: https://en.tradebearings.com/data/pdf/55/12/6806_2RS-157431.pdf ; price: https://ballsbearings.com/6806-2RS-Balls-Bearings-30mm-x-42mm-x-7mm-Sealed.htm |
| 1 | 6800-2RS 10×19×5 pitch idler | 0.005 | catalog | $2.99 | https://2mequipment.com/products/6800-2rs-ball-bearing-10x19x5mm-sealed ; mass: https://www.tradebearings.com/6800-2rs-the-rubber-thin-wall-deep-groove-ball-bearing-10x19x5mm-product-343163.html |
| 1 | RECOM **RP40-11012SFR/P-HC** (heat-sink variant, R-026), 43–160 V in → 12 V 3.33 A (40 W), 90.5 % | 0.043 | catalog | $137.93 | datasheet: https://recom-power.com/pdf/Powerline_DC-DC/RP40-FR.pdf ; price: https://www.unikeyic.com/products/dc-dc-power-modules/rp40-11012sfr-p/28724613.html |
| 3 | Input filter cap (RP40 datasheet note 9): Rubycon **200BXF68MEFC12.5X20**, 68 µF / 200 V, 12.5×20 mm radial | 0.0035 [EST] (no published mass) | [EST] | $0.77 | https://www.sinlinelec.com/part-item/02773665-200BXF68MEFC12-5X20.html |
| 2 | Input TVS (note 9): Littelfuse **SMDJ90A**, 90 V standoff, 146 V clamp, 3 kW, DO-214AB | 0.00021 | catalog | $0.744 | mass: https://www.littelfuse.com/assetdocs/tvs-diode-smdj-hr-datasheet?assetguid=fd159cdf-7edc-4d31-8ea5-8408d127b2c6 ; price: https://www.unikeyic.com/products/esd-suppressors/smdj90a/12384226.html |
| 1 | Filter carrier PCB (FR4, ~40×30 mm) | 0.005 [EST] | [EST] | [EST] $10 | — |
| 1 | CF shell 1.2 mm, ACP 5.8 oz 2×2 twill RTS prepreg (6 plies), on a machined 6061 mould | 0.179 | calc | prepreg $122 per listing; mould [EST] $400 | https://acpcomposites.com/shop/carbon-fiber/carbon-prepregs/5-8-oz-carbon-fiber-2x2-twill-weave-rts-prepreg |
| 1 | Neck yoke + shaft, machined from 1/2"×6"×6" 7075-T651 plate | 0.110 | [EST] mass | stock $19.32; machining [EST] $160 | https://noxmetals.co/products/7075-t651-plate-0-5x6x6-inch |
| 1 | Head deck, 1/8" (3.2 mm) 7075-T6 sheet, waterjet + pocket (was 6061) | 0.070 | [EST] mass | stock $42.96 (stock sheet); cutting [EST] $40 | https://www.onlinemetals.com/en/buy/aluminum/0-125-aluminum-sheet-7075-t6/pid/12663 |
| 1 | Pitch gravity torsion spring, Lee Spring LTL stock series, 302 SS, ~0.5 N·m @90° | 0.010 | [EST] | price on quote (catalog price-group) [EST] $15 | https://www.leespring.com/torsion-springs |
| — | Harness (RS485 + 12 V), GMSL2 FAKRA cable, fasteners | 0.060 | [EST] | [EST] $80 | — |
| | **Head + neck line total** | **0.833** | catalog 0.388 / calc 0.179 / EST 0.266 (incl. input filter 0.0159: caps 0.0105 EST, TVS 0.0004 catalog, PCB 0.005 EST) | ≈ $1,949 (+ mould) | |

**Brain area (booked by the Arbiter in R-025, not part of this line):** Connect Tech **JCB022** (MAX9296A GMSL2) or **JCB009** (MAX96792A GMSL3/2) camera board on the AGX301 MIPI expansion connector, **+0.045 kg** (CTIM-00143), PoC to the ZED. Open: ZED X Mini driver support on a CTI deserializer; the fallback is a Stereolabs ZED Link card.

Flags: the RP40 delivers 3.33 A, but two XM430s stalling at once draw 4.6 A. Set Dynamixel current limits to 1.5 A each (3.0 A total, inside the rating; gaze duty is about 0.2 A average). The RP40's 43 V minimum input is well below the pack's 68 V minimum.

**Required firmware setting (R-026 A27):** each neck XM430-W350-R must have **Current Limit (control table addr 38) set to 1.5 A** (≈ 560 units at 2.69 mA/unit), written at commissioning and verified at every boot by the brain before torque enable. Reason: 2 × 2.3 A stall = 4.6 A exceeds the RP40's 3.33 A.

Input filter notes: the TVS 90 V standoff is above the 84 V pack maximum, and its 146 V clamp is below the RP40's 160 V input maximum. The BXF 68 µF/200 V part is listed "Not For New Designs / Obsolete" at distributors, so pick an equivalent 68 µF ≥160 V 105 °C radial before purchase.
