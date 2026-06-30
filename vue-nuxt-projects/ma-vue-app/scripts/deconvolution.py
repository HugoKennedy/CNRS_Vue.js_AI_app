import json
import sys


def main():
    payload = json.load(sys.stdin)
    data = payload.get("data", {})
    parameters = payload.get("parameters", {})

    signal = data.get("signal_filtre") or data.get("signal", [])
    lambda_value = float(parameters.get("lambda", 0.01))

    signal_deconvolue = [
        round(value / (1 + lambda_value), 4)
        for value in signal
    ]

    output = {
        **data,
        "signal_deconvolue": signal_deconvolue,
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()