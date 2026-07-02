import json
import math
import sys


def main():
    payload = json.load(sys.stdin)
    parameters = payload.get("parameters", {})

    amplitude = float(parameters.get("amplitude", 1.0))
    duration_ms = float(parameters.get("duration_ms", 100.0))
    sampling_ms = float(parameters.get("sampling_ms", 1.0))
    freq_signal_hz = float(parameters.get("freq_signal_hz", 20.0))
    freq_noise_hz = float(parameters.get("freq_noise_hz", 250.0))
    noise_amplitude = float(parameters.get("noise_amplitude", 0.35))

    sample_count = int(duration_ms / sampling_ms) + 1

    time = []
    signal = []

    for index in range(sample_count):
        t_ms = index * sampling_ms
        t_s = t_ms / 1000.0

        slow_signal = amplitude * math.sin(2 * math.pi * freq_signal_hz * t_s)
        fast_noise = noise_amplitude * math.sin(2 * math.pi * freq_noise_hz * t_s)
        value = slow_signal + fast_noise

        time.append(round(t_ms, 4))
        signal.append(round(value, 6))

    output = {
        **payload.get("data", {}),
        "__thinkml_label": "Entree RC",
        "__thinkml_description": "Genere un signal sinusoidal bruite pour tester un filtre RC passe-bas.",
        "__thinkml_parameters": {
            "amplitude": amplitude,
            "duration_ms": duration_ms,
            "sampling_ms": sampling_ms,
            "freq_signal_hz": freq_signal_hz,
            "freq_noise_hz": freq_noise_hz,
            "noise_amplitude": noise_amplitude,
        },
        "time": time,
        "signal": signal,
        "signal_entree": signal,
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()