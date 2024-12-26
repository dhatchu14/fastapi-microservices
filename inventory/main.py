from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel

app = FastAPI()

# Correct Redis connection setup
redis = get_redis_connection(
    host="redis-18181.crce179.ap-south-1-1.ec2.redns.redis-cloud.com",
    port=18181,
    password="xVuVPxABtlQjUFNcFp4jzZTNCPloeNGM",
    decode_responses=True
)

class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis

@app.get('/products')
def all():
    return Product.all_pks()