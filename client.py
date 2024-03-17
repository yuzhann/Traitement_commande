import httpx

from messgaeQueue import *

place_order_url = "http://127.0.0.1:8000/place_order/4"

# Input data by user
order_data = [
    {
        "product_id": 1,
        "quantity": 10
    },
    {
        "product_id": 2,
        "quantity": 500
    }
]


# Post query
def handle_httpx(url, data):
    with httpx.Client() as client:
        response = client.post(url, json=data)
    return response, response.json()


# Send confirmation query
def handle_confirm_order(order_id, choice):
    confirm_order_url = f"http://127.0.0.1:8000/confirm_order/{order_id}?choice={choice}"
    response, message = handle_httpx(confirm_order_url, None)
    if response.status_code == 200:
        print(message)
    else:
        print(f"Failed to confirm order {order_id}.")


def main():
    response, message = handle_httpx(place_order_url, order_data)
    print(message)
    if response.status_code == 200:
        receive_message("order")
    else:
        print(f"Failed to confirm order.")


if __name__ == '__main__':
    main()
