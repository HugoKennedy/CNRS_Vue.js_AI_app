import json
import sys


def main():
    payload = json.load(sys.stdin)
    data = payload.get("data", {})

    spectrum = data.get("spectre", [])
    score = max(spectrum) if spectrum else 0

    if score > 10:
        predicted_class = "signal_fort"
    elif score > 3:
        predicted_class = "signal_normal"
    else:
        predicted_class = "signal_faible"

    output = {
        **data,
        "classes": [predicted_class],
        "classification_score": round(score, 4),
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()