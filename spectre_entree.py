import json
import math
import sys


def main():
    payload = json.load(sys.stdin)
    data = payload.get("data", {})
    parameters = payload.get("parameters", {})

    duration_s = float(parameters.get("duration_s", 1.0))
    sampling_hz = float(parameters.get("sampling_hz", 200.0))
    amplitude_1 = float(parameters.get("amplitude_1", 1.0))
    frequency_1_hz = float(parameters.get("frequency_1_hz", 10.0))
    amplitude_2 = float(parameters.get("amplitude_2", 0.5))
    frequency_2_hz = float(parameters.get("frequency_2_hz", 35.0))

    sample_count = int(duration_s * sampling_hz)

    time = []
    signal = []

    for index in range(sample_count):
        t = index / sampling_hz

        value_1 = amplitude_1 * math.sin(2 * math.pi * frequency_1_hz * t)
        value_2 = amplitude_2 * math.sin(2 * math.pi * frequency_2_hz * t)
        value = value_1 + value_2

        time.append(round(t, 6))
        signal.append(round(value, 6))

    output_metadata = data.get("__thinkml_outputs", {})

    output = {
        **data,
        "__thinkml_label": "Entree spectrale",
        "__thinkml_description": "Genere un signal compose de deux sinusoides.",
        "__thinkml_inputs": [],
        "__thinkml_parameters": {
            "duration_s": duration_s,
            "sampling_hz": sampling_hz,
            "amplitude_1": amplitude_1,
            "frequency_1_hz": frequency_1_hz,
            "amplitude_2": amplitude_2,
            "frequency_2_hz": frequency_2_hz,
        },
        "__thinkml_outputs": {
            **output_metadata,
            "signal": {
                "label": "Signal temporel",
                "unit": "V",
                "xKey": "time",
                "xLabel": "Temps",
                "xUnit": "s",
            },
            "sampling_hz": {
                "label": "Frequence d echantillonnage",
                "unit": "Hz",
            },
        },
        "time": time,
        "sampling_hz": sampling_hz,
        "signal": signal,
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()