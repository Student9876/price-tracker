from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union
from core.config import settings

import asyncio  # ADDED
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from core import security
import crud_operations as crud_operations
from api.deps import get_current_user
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scheduler import check_all_prices


# Database imports
from db.session import SessionLocal, engine
from db.base import Base
import models.user  # Import the user model file
import models.product  # ADDED: ensure Product mapper is loaded
import models.price_history  # ADDED: ensure PriceHistory is defined before mapper configuration

# Schema imports
import schemas as schemas

# Security and scraping imports 
from core.security import get_password_hash
from scrapers.factory import scrape_url

# Create all database tables (run this once)
Base.metadata.create_all(bind=engine)



# --- LIFESPAN FUNCTION ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on startup
    scheduler = AsyncIOScheduler()
    # Schedule check_all_prices to run every X minutes
    # !!! CHANGE interval for testing !!!
    scheduler.add_job(check_all_prices, "interval", minutes=1440, misfire_grace_time=30)
    scheduler.start()
    print("Scheduler has been started...")
    yield
    # This code runs on shutdown
    scheduler.shutdown()
    print("Scheduler has been shut down.")




app = FastAPI(
    title="Price Tracker API",
    description="API for tracking product prices and managing users.",
    lifespan=lifespan # Add the lifespan manager here
)


origins = [
    "http://localhost:3000", # Your Next.js frontend
    "https://price-tracker-ashen.vercel.app"
]

# 3. Add the CORSMiddleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods
    allow_headers=["*"], # Allow all headers
)



# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




# --- User and Auth Endpoints ---
@app.post("/auth/register", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.user.User).filter(
        models.user.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = models.user.User(
        email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/auth/login", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    # Authenticate the user
    user = security.authenticate_user(
        db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create the access token
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.user.User = Depends(get_current_user)):
    """
    Fetch the data for the currently authenticated user.
    """
    return current_user

# --- Scraper Endpoint ---
@app.post("/scrape", response_model=List[Union[schemas.ProductDetails, schemas.ErrorResponse]])
async def scrape_products(request: schemas.ScrapeRequest):
    # Note: We will protect this endpoint later
    if not request.urls:
        raise HTTPException(
            status_code=400, detail="URL list cannot be empty.")

    tasks = [scrape_url(str(url)) for url in request.urls]
    results = await asyncio.gather(*tasks)

    return results


@app.get("/track", response_model=List[schemas.TrackedProductResponse])
def get_tracked_products(
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(get_current_user)
):
    """
    Fetches a list of all products the currently authenticated user is tracking.
    """
    return crud_operations.get_tracked_products_for_user(db=db, user_id=current_user.id)


@app.post("/track", response_model=schemas.ProductDetails)
async def track_product(
    request: schemas.ScrapeRequest,
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(get_current_user)
):
    url_to_track = str(request.urls[0])  # Assuming one URL for now

    # 1. Scrape the URL to get product details
    scraped_data = await scrape_url(url_to_track)
    if isinstance(scraped_data, schemas.ErrorResponse):
        raise HTTPException(
            status_code=400, detail=f"Could not scrape URL: {scraped_data.error}")

    # 2. Check if this product already exists in our 'products' table
    product = crud_operations.get_product_by_signature(
        db, signature=scraped_data.signature)
    if not product:
        # If not, create it
        product = crud_operations.create_product(
            db, scraped_product=scraped_data)

    # 3. Create the link between the user and the product
    crud_operations.create_tracked_product_for_user(
        db=db,
        user=current_user,
        product=product,
        listing=scraped_data.listing  # <-- UPDATED LINE
    )

    return scraped_data


@app.get("/track/{tracked_product_id}", response_model=schemas.SingleTrackedProductResponse)
def get_single_tracked_product(
    tracked_product_id: int,
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(get_current_user)
):
    """
    Fetches the full details of a single product a user is tracking.
    """
    db_tracked_product = crud_operations.get_tracked_product_by_id(
        db, tracked_product_id=tracked_product_id, user_id=current_user.id
    )
    if db_tracked_product is None:
        raise HTTPException(status_code=404, detail="Tracked product not found")
    return db_tracked_product


@app.get("/track/{tracked_product_id}/history", response_model=List[schemas.PriceHistoryPoint])
def get_product_price_history(
    tracked_product_id: int,
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(get_current_user)
):
    """
    Fetches the price history for a single tracked product for charts.
    """
    db_tracked_product = crud_operations.get_tracked_product_by_id(
        db, tracked_product_id=tracked_product_id, user_id=current_user.id
    )
    if db_tracked_product is None:
        raise HTTPException(status_code=404, detail="Tracked product not found")
    return db_tracked_product.price_history


@app.delete("/track/{tracked_product_id}", response_model=schemas.Msg)
def delete_tracked_product(
    tracked_product_id: int,
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(get_current_user)
):
    """
    Stops tracking (deletes) a product for the current user.
    """
    deleted_product = crud_operations.delete_tracked_product(
        db, tracked_product_id=tracked_product_id, user_id=current_user.id
    )
    if deleted_product is None:
        raise HTTPException(status_code=404, detail="Tracked product not found")
    return {"msg": "Product removed successfully from tracking list"}