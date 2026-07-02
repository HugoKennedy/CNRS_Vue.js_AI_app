import json
import math
import sys


def compute_spectrum(signal, sampling_hz):
    sample_count = len(signal)

    if sample_count == 0:
        return [], []

    max_bin = sample_count // 2
    frequencies = []
    spectrum = []

    for frequency_index in range(max_bin):
        real_part = 0
        imaginary_part = 0

        for sample_index, value in enumerate(signal):
            angle = 2 * math.pi * frequency_index * sample_index / sample_count
            real_part += value * math.cos(angle)
            imaginary_part -= value * math.sin(angle)

        magnitude = math.sqrt(real_part ** 2 + imaginary_part ** 2)
        frequency_hz = frequency_index * sampling_hz / sample_count

        frequencies.append(round(frequency_hz, 4))
        spectrum.append(round(magnitude, 6))

    return frequencies, spectrum


def main():
    payload = json.load(sys.stdin)
    data = payload.get("data", {})

    sampling_hz = float(data.get("sampling_hz", 200.0))
    signal = data.get("signal_fenetre") or data.get("signal", [])

    frequencies, spectrum = compute_spectrum(signal, sampling_hz)

    output_metadata = data.get("__thinkml_outputs", {})

    output = {
        **data,
        "__thinkml_label": "Spectre",
        "__thinkml_description": "Calcule un spectre simple par transformee de Fourier discrete.",
        "__thinkml_inputs": ["signal_fenetre"],
        "__thinkml_parameters": {},
        "__thinkml_outputs": {
            **output_metadata,
            "spectre": {
                "label": "Spectre du signal",
                "unit": "amplitude",
                "xKey": "frequencies",
                "xLabel": "Frequence",
                "xUnit": "Hz",
            },
        },
        "frequencies": frequencies,
        "spectre": spectrum,
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()