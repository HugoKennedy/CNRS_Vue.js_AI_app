import json
import sys


def main():
    payload = json.load(sys.stdin)
    data = payload.get("data", {})

    signal_entree = data.get("signal_entree") or data.get("signal", [])
    signal_sortie = data.get("signal_sortie") or data.get("signal_filtre", [])

    if signal_entree:
        amplitude_entree = max(signal_entree) - min(signal_entree)
    else:
        amplitude_entree = 0

    if signal_sortie:
        amplitude_sortie = max(signal_sortie) - min(signal_sortie)
    else:
        amplitude_sortie = 0

    if amplitude_entree != 0:
        gain_approx = amplitude_sortie / amplitude_entree
    else:
        gain_approx = 0

    output = {
        **data,
        "__thinkml_label": "Sortie RC",
        "__thinkml_description": "Prepare les grandeurs finales du filtre RC pour affichage dans ThinkML.",
        "__thinkml_parameters": {},
        "signal": signal_entree,
        "signal_filtre": signal_sortie,
        "signal_sortie": signal_sortie,
        "gain_approx": round(gain_approx, 6),
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()