import json
import math
import sys
import time


def main():
    payload = json.load(sys.stdin)
    data = payload.get("data", {})

    signal = data.get("signal", [])
    sample_count = len(signal)

    signal_fenetre = []

    for index, value in enumerate(signal):
        if sample_count <= 1:
            coefficient = 1
        else:
            coefficient = 0.5 - 0.5 * math.cos(
                2 * math.pi * index / (sample_count - 1)
            )
        
        signal_fenetre.append(round(value * coefficient, 6))
    time.sleep(10)
    output_metadata = data.get("__thinkml_outputs", {})

    output = {
        **data,
        "__thinkml_label": "Fenetrage",
        "__thinkml_description": "Applique une fenetre de Hann avant le calcul du spectre.",
        "__thinkml_inputs": ["signal"],
        "__thinkml_parameters": {},
        "__thinkml_outputs": {
            **output_metadata,
            "signal_fenetre": {
                "label": "Signal fenetre",
                "unit": "V",
                "xKey": "time",
                "xLabel": "Temps",
                "xUnit": "s",
            },
        },
        "signal_fenetre": signal_fenetre,
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()