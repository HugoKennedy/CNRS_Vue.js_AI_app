import json
import sys


def main():
    payload = json.load(sys.stdin)
    data = payload.get("data", {})
    parameters = payload.get("parameters", {})

    signal = data.get("signal_filtre") or data.get("signal", [])
    threshold = float(parameters.get("threshold", 0.8))

    max_value = max(signal) if signal else 0
    anomaly_score = min(1, max_value / threshold) if threshold else 0

    output = {
        **data,
        "anomaly_score": round(anomaly_score, 4),
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()