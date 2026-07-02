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

    output_metadata = data.get("__thinkml_outputs", {})

    output = {
        **data,
        "__thinkml_label": "Condensateur RC",
        "__thinkml_description": "Simule la tension aux bornes du condensateur, c est-a-dire la sortie du filtre RC.",
        "__thinkml_parameters": {
            "capacite_farads": capacite_farads,
        },
        "__thinkml_outputs": {
            **output_metadata,
            "capacite_farads": {
                "label": "Capacite",
                "unit": "F",
            },
            "tau_s": {
                "label": "Constante de temps tau",
                "unit": "s",
            },
            "frequence_coupure_hz": {
                "label": "Frequence de coupure",
                "unit": "Hz",
            },
            "signal_filtre": {
                "label": "Signal filtre",
                "unit": "V",
                "xKey": "time",
                "xLabel": "Temps",
                "xUnit": "ms",
            },
            "signal_sortie": {
                "label": "Tension de sortie Vout",
                "unit": "V",
                "xKey": "time",
                "xLabel": "Temps",
                "xUnit": "ms",
            },
            "tension_condensateur": {
                "label": "Tension condensateur",
                "unit": "V",
                "xKey": "time",
                "xLabel": "Temps",
                "xUnit": "ms",
            },
            "tension_resistance": {
                "label": "Tension resistance",
                "unit": "V",
                "xKey": "time",
                "xLabel": "Temps",
                "xUnit": "ms",
            },
            "courant_resistance": {
                "label": "Courant resistance",
                "unit": "A",
                "xKey": "time",
                "xLabel": "Temps",
                "xUnit": "ms",
            },
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