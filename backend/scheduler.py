import asyncio
from sqlalchemy.orm import Session

from db.session import SessionLocal
import backend.crud_operations as crud_operations
from backend.scraper import scrape_url
import backend.schemas as schemas

async def check_all_prices():
    """
    The main job that runs on a schedule. It fetches all active tracked products,
    concurrently re-scrapes them, and saves the new price history.
    """
    print("SCHEDULER: Running daily price check...")
    db: Session = SessionLocal()

    try:
        tracked_items = crud_operations.get_all_active_tracked_products(db)
        if not tracked_items:
            print("SCHEDULER: No active products to track.")
            return

        # Create a list of scraping tasks to run concurrently
        tasks = [scrape_url(item.url) for item in tracked_items]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for item, result in zip(tracked_items, results):
            if isinstance(result, schemas.ProductDetails) and result.listing.price is not None:
                new_price = result.listing.price

                # Always save the new price to the history table
                crud_operations.add_price_history_record(db, tracked_product_id=item.id, price=new_price)

                # Check for a price drop and update the main record
                if new_price < item.current_price:
                    print(f"PRICE DROP! Item: {item.product.name}, Old: {item.current_price}, New: {new_price}")
                    crud_operations.update_tracked_product_price(db, tracked_product_id=item.id, new_price=new_price)
                    # TODO: Add notification logic here (e.g., send_email)
                else:
                     print(f"Price check for {item.product.name}: No drop. Current: {new_price}")

            elif isinstance(result, Exception):
                print(f"SCHEDULER: Error scraping {item.url}: {result}")
    finally:
        db.close()
        print("SCHEDULER: Job finished.")