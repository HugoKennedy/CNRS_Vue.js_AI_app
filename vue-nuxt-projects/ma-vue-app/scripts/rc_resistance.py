import json
import sys


def main():
    payload = json.load(sys.stdin)
    data = payload.get("data", {})
    parameters = payload.get("parameters", {})

    resistance_ohm = float(parameters.get("resistance_ohm", 1000.0))
    signal_entree = data.get("signal_entree") or data.get("signal", [])

    output_metadata = data.get("__thinkml_outputs", {})

    output = {
        **data,
        "__thinkml_label": "Resistance RC",
        "__thinkml_description": "Definit la resistance R du filtre RC passe-bas.",
        "__thinkml_parameters": {
            "resistance_ohm": resistance_ohm,
        },
        "__thinkml_outputs": {
            **output_metadata,
            "resistance_ohm": {
                "label": "Resistance",
                "unit": "Ohm",
            },
            "signal_apres_resistance": {
                "label": "Signal apres resistance",
                "unit": "V",
                "xKey": "time",
                "xLabel": "Temps",
                "xUnit": "ms",
            },
        },
        "resistance_ohm": resistance_ohm,
        "signal_apres_resistance": signal_entree,
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()