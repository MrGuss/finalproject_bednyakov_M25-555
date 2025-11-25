from .config import ParserConfig
from datetime import datetime
import json
config = ParserConfig()


def save_rates(rates: dict, request_s: float):
    try:
        with open(f"{config.rates_path}", "r") as f:
            rates_json_old = json.load(f)
    except FileNotFoundError:
        print("File not found")
        rates_json_old = {"pairs": {}, "last_refresh": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    except json.JSONDecodeError:
        print("File not found")
        rates_json_old = {"pairs": {}, "last_refresh": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    rates_json = {
        "pairs": rates,
        "last_refresh": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    rates_json_old["pairs"].update(rates_json["pairs"])
    rates_json_old["last_refresh"] = rates_json["last_refresh"]

    with open(f"{config.rates_path}", "w") as f:
        json.dump(rates_json_old, f, indent=2)

    try:
        with open(f"{config.exchange_path}", "r") as f:
            exchange_rates_json_old = json.load(f)
    except FileNotFoundError:
        exchange_rates_json_old = []
    except json.JSONDecodeError:
        exchange_rates_json_old = []

    exchange_rates_json = [
        {
            "id": f"{key}_{value['source']}",
            "from_currency": key.split("_")[0],
            "to_currency": key.split("_")[1],
            "rate": value["rate"],
            "timestamp": value["updated_at"],
            "source": value["source"],
            "meta": {
                "raw_id": key.split("_")[0] if value["source"] == "exchange_rates" else config.CRYPTO_ID_MAP[key.split("_")[0]],
                "request_ms": request_s*1000,
            },
        }
        for key, value in rates.items()
    ]
    exchange_rates_json_old += exchange_rates_json
    with open(f"{config.exchange_path}", "w") as f:
        json.dump(exchange_rates_json_old, f, sort_keys=False, indent=2)
        f.write('\n')
