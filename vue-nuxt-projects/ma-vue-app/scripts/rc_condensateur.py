import json
import math
import sys


def main():
    payload = json.load(sys.stdin)
    data = payload.get("data", {})
    parameters = payload.get("parameters", {})

    resistance_ohm = float(
        data.get("resistance_ohm", parameters.get("resistance_ohm", 1000.0))
    )
    capacite_farads = float(parameters.get("capacite_farads", 0.000001))

    time = data.get("time", [])
    signal_entree = (
        data.get("signal_apres_resistance")
        or data.get("signal_entree")
        or data.get("signal")
        or []
    )

    if len(time) >= 2:
        dt_s = (time[1] - time[0]) / 1000.0
    else:
        dt_s = float(parameters.get("dt_s", 0.001))

    tau_s = resistance_ohm * capacite_farads

    if tau_s <= 0:
        alpha = 1.0
    else:
        alpha = dt_s / (tau_s + dt_s)

    tension_condensateur = []
    tension_resistance = []
    courant_resistance = []

    previous_vout = 0.0

    for vin in signal_entree:
        vout = previous_vout + alpha * (vin - previous_vout)
        vr = vin - vout
        current = vr / resistance_ohm if resistance_ohm != 0 else 0.0

        tension_condensateur.append(round(vout, 6))
        tension_resistance.append(round(vr, 6))
        courant_resistance.append(round(current, 9))

        previous_vout = vout

    if tau_s > 0:
        frequence_coupure_hz = 1 / (2 * math.pi * tau_s)
    else:
        frequence_coupure_hz = 0

    output = {
        **data,
        "__thinkml_label": "Condensateur RC",
        "__thinkml_description": "Simule la charge et la decharge du condensateur. La sortie du filtre est la tension aux bornes du condensateur.",
        "__thinkml_parameters": {
            "capacite_farads": capacite_farads,
        },
        "capacite_farads": capacite_farads,
        "tau_s": round(tau_s, 9),
        "frequence_coupure_hz": round(frequence_coupure_hz, 4),
        "signal_sortie": tension_condensateur,
        "signal_filtre": tension_condensateur,
        "tension_condensateur": tension_condensateur,
        "tension_resistance": tension_resistance,
        "courant_resistance": courant_resistance,
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()