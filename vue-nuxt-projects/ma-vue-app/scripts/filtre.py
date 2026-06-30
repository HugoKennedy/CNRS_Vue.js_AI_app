import json
import sys


def moving_average(values, window_size=3):
    filtered = []

    for index in range(len(values)):
        start = max(0, index - window_size + 1)
        window = values[start:index + 1]
        filtered.append(round(sum(window) / len(window), 4))

    return filtered


def main():
    payload = json.load(sys.stdin)
    data = payload.get("data", {})

    signal = data.get("signal", [])

    output = {
        **data,
        "signal_filtre": moving_average(signal),
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()