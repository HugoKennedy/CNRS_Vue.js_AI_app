import json
import math
import sys


def main():
    payload = json.load(sys.stdin)

    parameters = payload.get("parameters", {})
    amplitude = float(parameters.get("amplitude", 1))
    duration_ns = int(parameters.get("duration_ns", 100))
    sampling_ns = int(parameters.get("sampling_ns", 5))

    time = list(range(0, duration_ns + 1, sampling_ns))

    signal = []
    for t in time:
        x = t / duration_ns if duration_ns else 0
        pulse = amplitude * math.exp(-((x - 0.35) ** 2) / 0.01)
        noise = 0.05 * amplitude * math.sin(40 * x)
        signal.append(round(pulse + noise, 4))

    output = {
        **payload.get("data", {}),
        "time": time,
        "signal": signal,
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()