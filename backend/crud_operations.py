from sqlalchemy.orm import Session, joinedload
import schemas

# Use clear and distinct aliases for each model file
import models.user as user_model
import models.product as product_model
import models.price_history as price_history_model


# --- User CRUD Operations ---

def get_user_by_email(db: Session, email: str):
    """Fetches a single user from the database by their email address."""
    return db.query(user_model.User).filter(user_model.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    """Creates a new user record in the database."""
    db_user = user_model.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- Product CRUD Operations ---

def get_product_by_signature(db: Session, signature: str):
    return db.query(product_model.Product).filter(product_model.Product.signature == signature).first()

def create_product(db: Session, scraped_product: schemas.ProductDetails):
    db_product = product_model.Product(
        signature=scraped_product.signature,
        name=scraped_product.name,
        brand=scraped_product.brand,
        category_path=scraped_product.category_path,
        image_urls=[str(url) for url in scraped_product.image_urls],
        key_features=scraped_product.key_features,
        specifications=scraped_product.specifications
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def create_tracked_product_for_user(
    db: Session, user: user_model.User, product: product_model.Product, listing: schemas.ListingDetails
):
    db_tracked_product = product_model.TrackedProduct(
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
    # 2. Add .options(joinedload(...)) to the query to eagerly load product details
    return (
        db.query(product_model.TrackedProduct)
        .options(joinedload(product_model.TrackedProduct.product))
        .filter(product_model.TrackedProduct.owner_id == user_id)
        .all()
    )

def get_all_active_tracked_products(db: Session):
    """Fetches all tracked products that are currently active."""
    # FIXED: Use the 'product_model' alias
    return db.query(product_model.TrackedProduct).filter(product_model.TrackedProduct.is_active == True).all()

def add_price_history_record(db: Session, tracked_product_id: int, price: float):
    """Adds a new price entry to the history table."""
    # FIXED: Use the 'price_history_model' alias
    db_price_history = price_history_model.PriceHistory(
        tracked_product_id=tracked_product_id,
        price=price
    )
    db.add(db_price_history)
    db.commit()
    return db_price_history

def update_tracked_product_price(db: Session, tracked_product_id: int, new_price: float):
    """Updates the 'current_price' on the main tracked product record."""
    # FIXED: Use the 'product_model' alias
    db_tracked_product = db.query(product_model.TrackedProduct).filter(product_model.TrackedProduct.id == tracked_product_id).first()
    if db_tracked_product:
        db_tracked_product.current_price = new_price
        db.commit()
    return db_tracked_product

def get_tracked_product_by_id(db: Session, tracked_product_id: int, user_id: int):
    """Fetches a single tracked product by its ID, ensuring it belongs to the user."""
    # FIXED: Use the 'product_model' alias
    return db.query(product_model.TrackedProduct).filter(
        product_model.TrackedProduct.id == tracked_product_id,
        product_model.TrackedProduct.owner_id == user_id
    ).first()

def delete_tracked_product(db: Session, tracked_product_id: int, user_id: int):
    """Deletes a tracked product record if it exists and belongs to the user."""
    db_tracked_product = get_tracked_product_by_id(db, tracked_product_id=tracked_product_id, user_id=user_id)
    if db_tracked_product:
        db.delete(db_tracked_product)
        db.commit()
        return db_tracked_product
    return None