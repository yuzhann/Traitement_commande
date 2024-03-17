import json
from typing import List

import httpx

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

from database import *
from messgaeQueue import *

app = FastAPI()


# Define data model
class OrderItem(BaseModel):
    product_id: int
    quantity: int


class Order(BaseModel):
    order_id: int
    items: List[OrderItem]


def check_inventory(product_id, quantity) -> bool:
    # check if one product is on stock
    inventory_info = get_inventory_by_product_id(product_id)
    if not inventory_info:
        print(f"Product ID {product_id} - Stock info not found.")
    return inventory_info >= quantity


def check_order_inventory(order: Order) -> bool:
    # check if all products in one order are on stock
    for item in order.items:
        if not check_inventory(item.product_id, item.quantity):
            return False
    return True


# client place an order
@app.post("/place_order/{order_id}")
async def place_order(order_id: int, items: List[OrderItem], background_tasks: BackgroundTasks):
    place_order_db(order_id, items)
    order = Order(order_id=order_id, items=items)
    background_tasks.add_task(check_order, order, background_tasks)
    return {"message": "order received successfully."}


# Check order and do other background task
def check_order(order: Order, background_tasks: BackgroundTasks):
    if not check_order_inventory(order):
        status = "non valid"
        update_order_status(order.order_id, status)
        background_tasks.add_task(send_non_confirmation, order.order_id, background_tasks)

    else:
        status = "valid"
        update_order_status(order.order_id, status)
        background_tasks.add_task(calculate_estimate, order, background_tasks)


# if no sufficient inventory
def send_non_confirmation(order_id: int, background_tasks: BackgroundTasks):
    order_info = {
        "order_id": order_id,
        "estimate": 0
    }
    message = json.dumps(order_info)
    background_tasks.add_task(send_estimate, message)
    with httpx.Client() as client:
        response = client.post(f"http://127.0.0.1:8000/not_confirm/{order_id}")
    print(response.text)


# send estimate to message queue
def send_estimate(estimate: json):
    send_message("order", estimate)


# calculate estimate if in stock
def calculate_estimate(order: Order, background_tasks: BackgroundTasks):
    estimate = 0
    order_id = order.order_id
    for item in order.items:
        price = get_product_price_by_product_id(item.product_id)
        estimate += price * item.quantity
    update_order_estimate(order_id, estimate)
    order_info = {
        "order_id": order_id,
        "estimate": estimate
    }
    message = json.dumps(order_info)
    background_tasks.add_task(send_estimate, message)


@app.post("/confirm_order/{order_id}")
async def confirm_order(order_id: int, choice: int):
    if choice == 1:
        # user accept order
        status = "confirmed"
        update_order_status(order_id, status)
        print("order confirmed")
        return {"message": f"Order {order_id} has been confirmed"}
    elif choice == 2:
        # user don't accept order
        status = "not confirmed"
        update_order_status(order_id, status)
        print("Order not confirmed.")
        return {"message": f"Order {order_id} has not been confirmed because user refused"}
    else:
        # not sufficient inventory
        return {"message": f"Order {order_id} has not been confirmed because of insufficient inventory"}
