import time
import requests
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request  

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*'],
)
redis = get_redis_connection(
    host="redis-16692.c264.ap-south-1-1.ec2.cloud.redislabs.com",
    port="16692",
    password="4qgkCyeLOdhaCm92zRICrLA7zIwJtGEq"
)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: float
    status: str

    class Meta:
        database = redis
    
def format(pk: str):
    ord = Order.get(pk)
    return {
        "id": ord.product_id,
        "price": ord.price,
        "fee": ord.fee,
        "total": ord.total,
        "quantity": ord.quantity,
        "status": ord.status
    }

@app.get('/orders/{pk}')
def get(pk:str):
    order = Order.get(pk)
    redis.xadd('refund_order',order.dict(),'*')
    return order

@app.delete("/orders/{pk}")
def delete(pk: str):
    return Order.delete(pk)

@app.get("/orders")
def all():
    return [format(pk) for pk in Order.all_pks()]

@app.post('/orders')
async def create(request: Request, background_tasks:BackgroundTasks):
    body = await request.json()
    # import pdb; pdb.set_trace()
    req = requests.get(f'http://localhost:8080/products/{body["id"]}')
    product = req.json()
    
    order = Order(
        product_id = body['id'],
        price = product['price'],
        fee = 0.2*product['price'],
        total = 1.2*product['price'],
        quantity = body['quantity'],
        status='pending'
    )
    order.save()
    background_tasks.add_task(order_completed,order)
    return order

def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()
    redis.xadd('order_completed',order.dict(),'*')

if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, reload=True, host='0.0.0.0')