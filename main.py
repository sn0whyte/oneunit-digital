import requests
import time
import os

API_KEY = os.getenv("API_KEY")
CAMPAIGN_ID = "149132406"

headers = {
    "Api-Key": API_KEY
}

processed_orders = set()

while True:
    try:
        print("Проверка заказов...")

        response = requests.get(
            f"https://api.partner.market.yandex.ru/campaigns/{CAMPAIGN_ID}/orders?fromDate=22-05-2026&toDate=23-05-2026",
            headers=headers
        )

        data = response.json()
        print(data)

        orders = data.get("orders", [])

        for order in orders:
            order_id = order["id"]

            if order_id in processed_orders:
                continue

            if order.get("status") == "PROCESSING":
                print(f"Найден заказ в обработке: {order_id}")

                item_id = order["items"][0]["id"]

                body = {
                    "items": [
                        {
                            "id": item_id,
                            "codes": ["ONEUNIT20"],
                            "activate_till": "2026-12-31",
                            "slip": "Здравствуйте!\n\nСпасибо за покупку цифрового сертификата OneUnit.\n\nПеред применением промокода убедитесь, что вы подписаны на магазин OneUnit.\n\nВаш промокод на скидку 20%:\nONEUNIT20\n\nКак воспользоваться:\n1. Перейдите в магазин OneUnit\n2. Выберите нужный товар\n3. Добавьте товар в корзину\n4. При оформлении заказа примените промокод ONEUNIT20\n\nВажно:\n— Воспользоваться промокодом можно через 24 часа после покупки сертификата\n— Скидка действует на ассортимент магазина OneUnit\n— Скидка не суммируется с другими акциями и промокодами\n\nПриятных покупок!"
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

                print(f"Ответ API по заказу {order_id}: {send.status_code}")
                print(send.text)

                processed_orders.add(order_id)

        time.sleep(60)

    except Exception as e:
        print("Ошибка:", e)
        time.sleep(60)
