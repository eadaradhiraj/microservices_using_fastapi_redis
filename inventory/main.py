from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
import uvicorn

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

class Product(HashModel):
    name:str
    price:float
    quantity:int

    class Meta:
        database = redis

@app.get("/products")
def all():
    return [format(pk) for pk in Product.all_pks()]

@app.get("/products/{pk}")
def get(pk: str):
    return Product.get(pk)

@app.delete("/products/{pk}")
def delete(pk: str):
    return Product.delete(pk)

def format(pk: str):
    product = Product.get(pk)
    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity,
    }

@app.post('/products')
def create(product: Product):
    return product.save()

if __name__ == '__main__':
    uvicorn.run("main:app", port=8080, reload=True,host='0.0.0.0')