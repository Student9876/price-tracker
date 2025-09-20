from sqlalchemy.orm import Session
import models.user as models
import schemas

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

# You will add more CRUD functions here later, for example:
# def create_tracked_product_for_user(...)
# def get_tracked_products_for_user(...)