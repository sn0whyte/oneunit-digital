import os
import requests
from datetime import datetime, timezone
from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
CAMPAIGN_ID = "149132406"


def ok_response():
    return jsonify({
        "name": "digital",
        "version": "1.0",
        "time": datetime.now(timezone.utc).isoformat(),
        "status": "OK"
    }), 200


def get_promo_by_sku(shop_sku):

    if shop_sku == "Подарочный сертификат 18%":
        return "ONEUNIT18", "18%"

    if shop_sku == "Подарочный сертификат 10%":
        return "ONEUNIT10", "10%"

    return "ONEUNIT18", "18%"


@app.route("/", methods=["GET"])
def home():
    return "OK", 200


@app.route("/webhook", methods=["POST"])
@app.route("/webhook/notification", methods=["POST"])
def webhook():

    data = request.json

    print("Webhook:", data)

    if not data:
        return ok_response()

    if data.get("notificationType") == "PING":
        return ok_response()

    order_id = (
        data.get("orderId")
        or data.get("order", {}).get("id")
        or data.get("id")
    )

    if not order_id:
        return ok_response()

    try:

        order_response = requests.get(
            f"https://api.partner.market.yandex.ru/v2/campaigns/{CAMPAIGN_ID}/orders/{order_id}",
            headers={
                "Api-Key": API_KEY
            }
        )

        order_data = order_response.json()
        print("Order:", order_data)

        order = order_data.get("order", {})

        if order.get("status") != "PROCESSING":
            return ok_response()

        item = order["items"][0]

        item_id = item["id"]
        shop_sku = item.get("shopSku", "")

        print("SHOP SKU:", shop_sku)

        promo_code, discount = get_promo_by_sku(shop_sku)

        slip_text = f"""
Спасибо за покупку сертификата OneUnit!

━━━━━━━━━━━━━━━━━━
Ваш промокод:
{promo_code}
━━━━━━━━━━━━━━━━━━

Размер скидки:
{discount}

Промокод активируется через 24 часа.

Срок действия:
6 месяцев с момента получения.

Как использовать:
1. Перейдите в магазин OneUnit
2. Выберите нужный товар
3. Добавьте товар в корзину
4. При оформлении заказа примените промокод {promo_code}

Важно:
• Перед применением убедитесь, что вы подписаны на магазин OneUnit
• Скидка не суммируется с другими акциями
• Один промокод можно использовать один раз

Спасибо за покупку!
OneUnit
"""

        body = {
            "items": [
                {
                    "id": item_id,
                    "codes": [promo_code],
                    "activate_till": "2026-12-31",
                    "slip": slip_text
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

        print("Promo:", promo_code)
        print("Deliver response:", send.status_code)
        print(send.text)

    except Exception as e:
        print("ERROR:", e)

    return ok_response()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
