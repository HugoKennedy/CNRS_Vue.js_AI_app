import json
import sys


def main():
    payload = json.load(sys.stdin)
    data = payload.get("data", {})

    raw_data = data.get("raw_data", [])

    if raw_data:
        average = sum(raw_data) / len(raw_data)
        minimum = min(raw_data)
        maximum = max(raw_data)
    else:
        average = 0
        minimum = 0
        maximum = 0

    output = {
        **data,
        "analysis": {
            "sample_count": len(raw_data),
            "average": round(average, 4),
            "minimum": round(minimum, 4),
            "maximum": round(maximum, 4),
        },
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()