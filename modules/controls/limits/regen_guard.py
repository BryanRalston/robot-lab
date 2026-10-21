"""Bus-voltage / regen guard per Electronics P-058 (d0a346c). Controls side of the logic; the hardware clamp (P-045) is Electronics'.
1) Bus >= 86 V: stop commanding regen (braking) torque on ALL joints and log. 88 V: hardware clamp. 92 V: XP[1] trip (pending WI[35]). Never reach 95 V.
2) Waist braking torque only when |w| <= min(5.75, D102c limits: 3.67 average / 5.86 momentary) rad/s. Above that, zero torque, MO stays 1.
3) Non-cell faults: don't request BMS open while any joint is above 5.98 rad/s; sequence SS1 -> STO -> open. Cell faults open immediately.
4) After any event above 88 V, log peak AN[6], clamp fire count and HS100 temperature."""
V_NO_REGEN, V_CLAMP, V_TRIP, V_MAX = 86.0, 88.0, 92.0, 95.0
W_WAIST_BRAKE_MAX = 5.75
W_BMS_OPEN_MAX = 5.98


def regen_allowed(v_bus):
    return v_bus < V_NO_REGEN


def is_regen(tau, w):
    return tau * w < 0.0


def guard_tau(names, tau, w, v_bus):
    """Zero regen torque per rules 1-2. names/tau/w are same-length lists; returns (tau, log)."""
    log = []
    for i, n in enumerate(names):
        if is_regen(tau[i], w[i]):
            if not regen_allowed(v_bus):
                log.append((n, 'bus>=86V', tau[i])); tau[i] = 0.0
            elif n.endswith('waist_pitch') and abs(w[i]) > W_WAIST_BRAKE_MAX:
                log.append((n, 'waist |w|>5.75', tau[i])); tau[i] = 0.0
    return tau, log


def bms_open_permitted(cell_fault, joint_speeds):
    return cell_fault or max(abs(x) for x in joint_speeds) <= W_BMS_OPEN_MAX
