# seed_db.py

import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Import your database session and models
from db.session import SessionLocal
import models.product as product_model
import models.price_history as price_history_model
import models.user as user_model # <-- ADD THIS LINE

# --- SCRIPT CONFIGURATION ---
# The ID of the item in your 'tracked_products' table you want to add history to.
# This is usually 1 if it's the first item you added.
TARGET_TRACKED_PRODUCT_ID = 9
NUMBER_OF_DAYS = 60 # How many days of history to generate

def seed_price_history():
    """
    Generates fake historical price data for a specific tracked product.
    """
    db: Session = SessionLocal()
    print(f"Attempting to seed price history for tracked_product_id={TARGET_TRACKED_PRODUCT_ID}...")

    try:
        # 1. Find the tracked product we want to add history to
        tracked_product = db.query(product_model.TrackedProduct).filter(
            product_model.TrackedProduct.id == TARGET_TRACKED_PRODUCT_ID
        ).first()

        if not tracked_product:
            print(f"Error: Could not find TrackedProduct with id={TARGET_TRACKED_PRODUCT_ID}.")
            print("Please make sure you have tracked at least one product.")
            return

        print(f"Found product: {tracked_product.product.name}. Generating {NUMBER_OF_DAYS} days of price data.")
        
        # 2. Generate and add fake price history records
        base_price = float(tracked_product.current_price)
        for i in range(NUMBER_OF_DAYS):
            # Create a fluctuating price around the base price
            price_fluctuation = base_price * random.uniform(-0.06, 0.06) # +/- 5%
            new_price = round(base_price + price_fluctuation, 2)

            # Create a timestamp for each of the previous days
            new_timestamp = datetime.now() - timedelta(days=i)

            # Create the new history record
            history_record = price_history_model.PriceHistory(
                tracked_product_id=tracked_product.id,
                price=new_price,
                timestamp=new_timestamp
            )
            db.add(history_record)

        # 3. Commit all the new records to the database
        db.commit()
        print(f"Successfully added {NUMBER_OF_DAYS} price history records.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_price_history()