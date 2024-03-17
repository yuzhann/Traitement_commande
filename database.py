from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
inventory_collection = db['inventory']
prices_collection = db['product_prices']
orders_collection = db['orders']

# initialized data
inventory = {
    1: 50,
    2: 100
}

product_prices = {
    1: 100,
    2: 200,
}

# Initialize database
for product_id, stock in inventory.items():
    inventory_collection.update_one(
        {"product_id": product_id},
        {"$set": {"stock": stock}},
        upsert=True
    )

for product_id, price in product_prices.items():
    prices_collection.update_one(
        {"product_id": product_id},
        {"$set": {"price": price}},
        upsert=True
    )


# Get stock of one product
def get_inventory_by_product_id(product_id: int):
    inventory_collection = db['inventory']
    stock_info = inventory_collection.find_one({"product_id": product_id})
    if stock_info:
        return stock_info['stock']
    else:
        return None


# Get price of one product
def get_product_price_by_product_id(product_id: int):
    prices_collection = db['product_prices']
    price_info = prices_collection.find_one({"product_id": product_id})
    if price_info:
        return price_info['price']
    else:
        return None


# Add one order
def place_order_db(order_id, items):
    items_dicts = [item.dict() for item in items]
    orders_collection.insert_one({
        "order_id": order_id,
        "items": items_dicts,
        "status": "placed",
        "estimate": 0
    })


# Update order status
def update_order_status(order_id, new_status):
    result = orders_collection.update_one(
        {"order_id": order_id},
        {"$set": {"status": new_status}},
        upsert=True
    )


# Update order estimate
def update_order_estimate(order_id, estimate):
    result = orders_collection.update_one(
        {"order_id": order_id},
        {"$set": {"estimate": estimate}},
        upsert=True
    )


# Update inventory
def update_inventory(product_id, quantity):
    inventory_collection.update_one(
        {"product_id": product_id},
        {"$set": {"stock": quantity}},
        upsert=True
    )
