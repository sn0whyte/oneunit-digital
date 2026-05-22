import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
CAMPAIGN_ID = "149132406"

SLIP_TEXT = """Здравствуйте!

Спасибо за покупку цифрового сертификата OneUnit.

Ваш промокод:
ONEUNIT20
"""


@app.route("/", methods=["GET"])
def home():
    return "OK", 200


@app.route("/webhook", methods=["POST", "GET"])
def webhook():

    if request.method == "GET":
        return "OK", 200

    data = request.json

    print("Webhook:", data)

    if not data:
        return jsonify({"ok": True}), 200

    order_id = (
        data.get("orderId")
        or data.get("order", {}).get("id")
        or data.get("id")
    )

    if not order_id:
        return jsonify({"ok": True}), 200

    order_response = requests.get(
        f"https://api.partner.market.yandex.ru/v2/campaigns/{CAMPAIGN_ID}/orders/{order_id}",
        headers={"Api-Key": API_KEY}
    )

    order_data = order_response.json()

    print("Order:", order_data)

    order = order_data.get("order", {})

    if order.get("status") != "PROCESSING":
        return jsonify({"ok": True}), 200

    item_id = order["items"][0]["id"]

    body = {
        "items": [
            {
                "id": item_id,
                "codes": ["ONEUNIT20"],
                "activate_till": "2026-12-31",
                "slip": SLIP_TEXT
            }
        ]
    }

    send = requests.post(
        f"https://api.partner.market.yandex.ru/v2/campaigns/{CAMPAIGN_ID}/orders/{order_id}/deliverDigitalGoods",
        headers={
            "Api-Key": API_KEY,
            "Content-Type": "application/json"
        },
        json=body
    )

    print("Deliver response:", send.status_code, send.text)

    return jsonify({"ok": True}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
