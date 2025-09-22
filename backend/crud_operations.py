from sqlalchemy.orm import Session
import models.user as models
import schemas as schemas
import models.product as product_models
# --- User CRUD Operations ---

def get_user_by_email(db: Session, email: str):
    """
    Fetches a single user from the database by their email address.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    """
    Creates a new user record in the database.
    """
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_product_by_signature(db: Session, signature: str):
    return db.query(product_models.Product).filter(product_models.Product.signature == signature).first()


def create_product(db: Session, scraped_product: schemas.ProductDetails):
    # This function now saves all the rich canonical data
    db_product = product_models.Product(
        signature=scraped_product.signature,
        name=scraped_product.name,
        brand=scraped_product.brand,
        category_path=scraped_product.category_path,
        image_urls=[str(url) for url in scraped_product.image_urls], # Convert HttpUrl to string
        key_features=scraped_product.key_features,
        specifications=scraped_product.specifications
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def create_tracked_product_for_user(
    db: Session, user: models.User, product: product_models.Product, listing: schemas.ListingDetails
):
    # This function now saves all the rich listing-specific data
    db_tracked_product = product_models.TrackedProduct(
        url=str(listing.url),
        initial_price=listing.price,
        current_price=listing.price,
        owner_id=user.id,
        product_id=product.id,
        mrp=listing.mrp,
        currency=listing.currency,
        stock_status=listing.stock_status,
        seller_name=listing.seller_name,
        average_rating=listing.average_rating,
        num_ratings=listing.num_ratings,
        offers=listing.offers
    )
    db.add(db_tracked_product)
    db.commit()
    db.refresh(db_tracked_product)
    return db_tracked_product

def get_tracked_products_for_user(db: Session, user_id: int):
    """
    Fetches all products a specific user is tracking.
    """
    return db.query(product_models.TrackedProduct).filter(product_models.TrackedProduct.owner_id == user_id).all()


def get_all_active_tracked_products(db: Session):
    """Fetches all tracked products that are currently active."""
    return db.query(models.product.TrackedProduct).filter(models.product.TrackedProduct.is_active == True).all()

def add_price_history_record(db: Session, tracked_product_id: int, price: float):
    """Adds a new price entry to the history table."""
    db_price_history = models.price_history.PriceHistory(
        tracked_product_id=tracked_product_id,
        price=price
    )
    db.add(db_price_history)
    db.commit()
    return db_price_history

def update_tracked_product_price(db: Session, tracked_product_id: int, new_price: float):
    """Updates the 'current_price' on the main tracked product record."""
    db_tracked_product = db.query(models.product.TrackedProduct).filter(models.product.TrackedProduct.id == tracked_product_id).first()
    if db_tracked_product:
        db_tracked_product.current_price = new_price
        db.commit()
    return db_tracked_product