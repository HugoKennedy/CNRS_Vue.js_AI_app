import json
import sys


def main():
    payload = json.load(sys.stdin)
    data = payload.get("data", {})

    frequencies = data.get("frequencies", [])
    spectrum = data.get("spectre", [])

    dominant_frequency_hz = 0
    dominant_amplitude = 0

    if frequencies and spectrum:
        start_index = 1 if len(spectrum) > 1 else 0
        search_values = spectrum[start_index:]

        if search_values:
            local_max = max(search_values)
            local_index = spectrum.index(local_max)

            dominant_frequency_hz = frequencies[local_index]
            dominant_amplitude = local_max

    output_metadata = data.get("__thinkml_outputs", {})

    output = {
        **data,
        "__thinkml_label": "Pic spectral",
        "__thinkml_description": "Detecte la frequence dominante dans le spectre.",
        "__thinkml_inputs": ["spectre", "frequencies"],
        "__thinkml_parameters": {},
        "__thinkml_outputs": {
            **output_metadata,
            "dominant_frequency_hz": {
                "label": "Frequence dominante",
                "unit": "Hz",
            },
            "dominant_amplitude": {
                "label": "Amplitude dominante",
                "unit": "amplitude",
            },
        },
        "dominant_frequency_hz": dominant_frequency_hz,
        "dominant_amplitude": round(dominant_amplitude, 6),
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()