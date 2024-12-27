from main import redis, Product  # Importing Redis connection and Product model from the main application
import time  # Importing time module for introducing delay

# Define the Redis stream key and group
key = 'order_completed'  # Stream where completed orders are logged
group = 'inventory-group'  # Consumer group for processing inventory updates

# Attempt to create a Redis consumer group
try:
    redis.xgroup_create(key, group)  # Create a consumer group for the stream
except:
    print('Group already exists!')  # Print message if the group already exists

# Infinite loop to continuously listen and process messages from the stream
while True:
    try:
        # Read messages from the Redis stream for the consumer group
        results = redis.xreadgroup(group, key, {key: '>'}, None)

        # Check if there are any new messages to process
        if results != []:
            for result in results:  # Iterate through the stream results
                obj = result[1][0][1]  # Extract the message object
                try:
                    # Fetch the product using the product_id from the message
                    product = Product.get(obj['product_id'])
                    # Deduct the ordered quantity from the product inventory
                    product.quantity = product.quantity - int(obj['quantity'])
                    product.save()  # Save the updated product back to the database
                except:
                    # If an error occurs (e.g., product not found), log the order for refund
                    redis.xadd('refund_order', obj, '*')  # Add the order to the refund stream

    except Exception as e:
        # Catch and print any exceptions during stream processing
        print(str(e))
    
    # Wait for 1 second before checking for new messages again
    time.sleep(1)
