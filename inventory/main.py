from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create a FastAPI app instance
app = FastAPI()

# Add middleware for handling Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],  # Allow requests from this origin (frontend)
    allow_methods=['*'],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=['*']   # Allow all headers
)

# Establish a connection to the Redis database
redis = get_redis_connection(
    host="redis-18181.crce179.ap-south-1-1.ec2.redns.redis-cloud.com",
    port=18181,
    password="xVuVPxABtlQjUFNcFp4jzZTNCPloeNGM",
    decode_responses=True  # Automatically decode Redis responses
)

# Define a Redis model for storing product details
class Product(HashModel):
    name: str      # Name of the product
    price: float   # Price of the product
    quantity: int  # Quantity available in stock

    class Meta:
        database = redis  # Specify the Redis connection for this model

# Define a Pydantic model for validating product input data
class ProductRequest(BaseModel):
    name: str      # Name of the product
    price: float   # Price of the product
    quantity: int  # Quantity of the product

# Endpoint to retrieve all products
@app.get('/products')
def all():
    return [format(pk) for pk in Product.all_pks()]  # Format and return all product primary keys

# Helper function to format product data into a dictionary
def format(pk: str):
    product = Product.get(pk)  # Fetch product from Redis using primary key
    return {
        'id': product.pk,      # Primary key (ID)
        'name': product.name,  # Product name
        'price': product.price,  # Product price
        'quantity': product.quantity  # Product quantity
    }

# Endpoint to create a new product
@app.post('/products')
def create(product: ProductRequest):
    # Create a new Product instance using the input data
    new_product = Product(
        name=product.name,
        price=product.price,
        quantity=product.quantity
    )
    new_product.save()  # Save the product in Redis
    return {
        "message": "Product created successfully",
        "product": {
            "id": new_product.pk,      # Return the new product's ID
            "name": new_product.name,  # Return the product name
            "price": new_product.price,  # Return the product price
            "quantity": new_product.quantity  # Return the product quantity
        }
    }

# Endpoint to retrieve a single product by its ID
@app.get('/products/{pk}')
def get(pk: str):
    return Product.get(pk)  # Fetch and return the product from Redis using its primary key

# Endpoint to delete a product by its ID
@app.delete('/products/{pk}')
def delete(pk: str):
    return Product.delete(pk)  # Delete the product from Redis and return the result

# Endpoint to update an existing product by its ID
@app.put('/products/{pk}')
def update(pk: str, product: ProductRequest):
    existing_product = Product.get(pk)  # Fetch the existing product
    # Update the product's fields with the new values
    existing_product.name = product.name
    existing_product.price = product.price
    existing_product.quantity = product.quantity
    existing_product.save()  # Save the updated product in Redis
    return {
        "message": "Product updated successfully",
        "product": {
            "id": existing_product.pk,      # Return the updated product's ID
            "name": existing_product.name,  # Return the updated product name
            "price": existing_product.price,  # Return the updated product price
            "quantity": existing_product.quantity  # Return the updated product quantity
        }
    }
