from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

# Correct Redis connection setup
redis = get_redis_connection(
    host="redis-18181.crce179.ap-south-1-1.ec2.redns.redis-cloud.com",
    port=18181,
    password="xVuVPxABtlQjUFNcFp4jzZTNCPloeNGM",
    decode_responses=True
)

# Define the Product model for Redis
class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis

# Define a Pydantic model for the request body
class ProductRequest(BaseModel):
    name: str
    price: float
    quantity: int

@app.get('/products')
def all():
    return [format(pk) for pk in Product.all_pks()]

def format(pk: str):
    product = Product.get(pk)
    return {
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }

@app.post('/products')
def create(product: ProductRequest):
    new_product = Product(
        name=product.name,
        price=product.price,
        quantity=product.quantity
    )
    new_product.save()
    return {
        "message": "Product created successfully",
        "product": {
            "id": new_product.pk,
            "name": new_product.name,
            "price": new_product.price,
            "quantity": new_product.quantity
        }
    }

@app.get('/products/{pk}')
def get(pk: str):
    return Product.get(pk)

@app.delete('/products/{pk}')
def delete(pk: str):
    return Product.delete(pk)

@app.put('/products/{pk}')
def update(pk: str, product: ProductRequest):
    existing_product = Product.get(pk)
    existing_product.name = product.name
    existing_product.price = product.price
    existing_product.quantity = product.quantity
    existing_product.save()
    return {
        "message": "Product updated successfully",
        "product": {
            "id": existing_product.pk,
            "name": existing_product.name,
            "price": existing_product.price,
            "quantity": existing_product.quantity
        }
    }
