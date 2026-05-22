```python
import requests
import time

API_KEY = "ACMA:EmkHOmUUfComIFAnHkVQrfEhRWuZxDoGHrRqU0hG:52df12e8"
CAMPAIGN_ID = "149132406"

headers = {
    "Api-Key": API_KEY
}

processed_orders = set()

while True:
    try:
        # Получаем заказы
        response = requests.get(
            f"https://api.partner.market.yandex.ru/campaigns/{CAMPAIGN_ID}/orders",
            headers=headers
        )

        orders = response.json().get("orders", [])

        for order in orders:
            order_id = order["id"]

            if order_id in processed_orders:
                continue

            if order["status"] == "PROCESSING":

                item_id = order["items"][0]["id"]

                body = {
                    "items": [
                        {
                            "id": item_id,
                            "codes": ["ONEUNIT20"],
                            "activate_till": "2026-12-31",
                            "slip": "Спасибо за покупку сертификата OneUnit!\n\nВаш промокод: ONEUNIT20\n\nПромокод активируется через 24 часа."
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

                print(f"Заказ {order_id} обработан:", send.status_code)

                processed_orders.add(order_id)

        time.sleep(60)

    except Exception as e:
        print(e)
        time.sleep(60)
```
