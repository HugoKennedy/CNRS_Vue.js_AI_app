import json
import sys

def main():
    payload = json.load(sys.stdin)
    data = payload.get("data", {})

    signal = data.get("signal", [])

    output = {
        **data,
        "signal_test": [value * 2 for value in signal],
    }

    print(json.dumps(output))

if __name__ == "__main__":
    main()