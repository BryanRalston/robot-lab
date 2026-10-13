# RFQ: ITECH IT6005C-80-150 battery emulator for the G5 regen bench (R-010)
Status: **DRAFT ONLY, nothing sent.** No email has been sent and no web form submitted. Bryan sends it himself, or approves a send.

## Quote route (found 2026-10-13)
| route | contact | source |
|---|---|---|
| US distributor (preferred: US invoice, local support) | **AV-TEK**, sales@avtekconsulting.com, +1 512-379-8121 / +1 281-938-1727. Offices: 4123 Hollister Suite G, Houston TX 77080, and 900 Barnes Dr Suite 200, San Marcos TX 78666. Mo–Fr 8–18 CT | avtekconsulting.com IT6000C product page |
| ITECH direct (HQ, Taiwan) | info@itechate.com, +886-3-6684333. No.918 Zhongzheng Rd, Zhonghe Dist., New Taipei City 235 | IT6000C catalogue (itechate.com/uploadfiles/catalogue/IT6000C-en.pdf) |
| ITECH web inquiry | "Inquiry" button on itechate.com/en/product/dc-power-supply/IT6000C.html | not used (no form submitted) |
Ask AV-TEK first. ITECH direct is the fallback if AV-TEK can't quote within a week, or to confirm the US channel.

## Spec list (what the bench needs; see BENCH_TEST_PLAN.md §2, §7)
- Model: **IT6005C-80-150** (80 V / ±150 A / ±5 kW, bidirectional, regenerative to grid ≤ 95 %). Alternative if 80 V headroom is a problem: next voltage class (IT6006C-300-75).
- Voltage: the bus runs 68–84 V and the chopper clamps at 88–90 V. **The 80 V class is below 84 V full charge.** Ask whether 84 V operation is possible. If not, quote the 300 V class.
- Current: ≥ ±40 A continuous. 30 A is the BMS charge limit and ~33 A the leg trunk peak.
- Mode: **battery simulation** (programmable internal resistance 60 mΩ, SOC/OCV curve upload for a 20S P45B pack, charge current limit 30 A). Ask about the ITECH battery-simulation software licence (BSS) and price.
- Dynamics: source↔sink transition without overshoot at 1 kHz-class current steps (gait regen pulses ~50–300 ms).
- Measurement/logging: V/I readback ≥ 1 kHz with timestamps, LAN/USB/CAN; external trigger/digital I/O for stride sync.
- Mains: 3-phase 400 V or 208 V (state site supply). Regen-to-grid permitted.
- Options to quote: rack kit, GPIB not needed, calibration certificate (ISO 17025), 3-year warranty, lead time, demo/rental unit availability.

## Ready-to-send RFQ text (for Bryan's approval; do not send without it)
To: sales@avtekconsulting.com
Cc: (optional) info@itechate.com
Subject: RFQ: ITECH IT6005C-80-150 bidirectional DC supply with battery simulation (robotics regen bench)

Hello AV-TEK team,

I'd like a quotation for an ITECH IT6000C bidirectional programmable DC power supply for a battery-emulation test bench. The bench measures regenerative energy from robot leg actuators on a 20S Li-ion bus.

Requested configuration:
1. IT6005C-80-150 (80 V / ±150 A / 5 kW) qty 1. Our bus spans 68–84 V (20S Li-ion, full charge 84 V). Please confirm whether the 80 V model can run at 84 V. If not, please also quote the IT6006C-300-75.
2. Battery simulation function/software (programmable internal resistance, OCV/SOC curve, charge-current limit), with licence pricing.
3. Readback/logging of at least 1 kHz with LAN/USB/CAN and digital I/O trigger.
4. Calibration certificate (ISO 17025 if available), rack-mount kit, and warranty options.

Please include unit price, lead time, shipping to [ship-to address], input power requirements (3-phase 208 V or 400 V), and whether a demo or rental unit is available for a 4-week test window starting [date].

Thank you,
Bryan Ralston
[company / address / phone]

## Expected price
[EST] $9–12 k for the 5 kW 80 V unit (no public price found; IT6000C family reseller listings show no model-specific price). Budget line stays in BENCH_TEST_PLAN.md §7 until the quote arrives.
