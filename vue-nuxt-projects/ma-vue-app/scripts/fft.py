import json
import math
import sys


def compute_simple_spectrum(signal):
    spectrum = []
    sample_count = len(signal)

    if sample_count == 0:
        return spectrum

    max_bins = min(20, sample_count)

    for frequency_index in range(max_bins):
        real_part = 0
        imaginary_part = 0

        for sample_index, value in enumerate(signal):
            angle = (2 * math.pi * frequency_index * sample_index) / sample_count
            real_part += value * math.cos(angle)
            imaginary_part -= value * math.sin(angle)

        magnitude = math.sqrt(real_part ** 2 + imaginary_part ** 2)
        spectrum.append(round(magnitude, 4))

    return spectrum


def main():
    payload = json.load(sys.stdin)
    data = payload.get("data", {})

    signal = data.get("signal_filtre") or data.get("signal", [])
    spectrum = compute_simple_spectrum(signal)

    output = {
        **data,
        "frequencies": list(range(len(spectrum))),
        "spectre": spectrum,
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()