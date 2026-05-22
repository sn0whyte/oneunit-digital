import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
CAMPAIGN_ID = "149132406"

SLIP_TEXT = """Здравствуйте!

Спасибо за покупку цифрового сертификата OneUnit.

Перед применением промокода убедитесь, что вы подписаны на магазин OneUnit.

Ваш промокод на скидку 20%:
ONEUNIT20

Воспользоваться промокодом можно через 24 часа после покупки сертификата.

Приятных покупок!
"""


@app.route("/", methods=["GET"])
def home():
    return "OneUnit webhook is running"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Webhook:", data)

    order_id = (
        data.get("orderId")
        or data.get("order", {}).get("id")
        or data.get("id")
    )

    if not order_id:
        return jsonify({"error": "order_id not found"}), 400

    order_response = requests.get(
        f"https://api.partner.market.yandex.ru/v2/campaigns/{CAMPAIGN_ID}/orders/{order_id}",
        headers={"Api-Key": API_KEY}
    )

    order_data = order_response.json()
    print("Order:", order_data)

    order = order_data.get("order", {})

    if order.get("status") != "PROCESSING":
        return jsonify({"ok": True, "message": "Order is not PROCESSING"}), 200

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

    return jsonify({
        "ok": True,
        "status_code": send.status_code,
        "response": send.text
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
