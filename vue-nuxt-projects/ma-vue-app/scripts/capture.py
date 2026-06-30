import json
import math
import sys


def main():
    payload = json.load(sys.stdin)
    parameters = payload.get("parameters", {})

    channel = int(parameters.get("channel", 1))

    raw_data = []
    for index in range(50):
        value = math.sin(index / 5) + channel * 0.1
        raw_data.append(round(value, 4))

    output = {
        **payload.get("data", {}),
        "raw_data": raw_data,
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()