from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union
from core.config import settings


from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from core import security
import db_crud # NEW

# Database imports
from db.session import SessionLocal, engine
from db.base import Base
import models.user # Import the user model file

# Schema imports
import schemas

# Security and scraping imports
from core.security import get_password_hash
from scraper import scrape_url

# Create all database tables (run this once)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Price Tracker API",
    description="API for tracking product prices and managing users."
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
    db_user = db.query(models.user.User).filter(models.user.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.user.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/auth/login", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    # Authenticate the user
    user = security.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create the access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}



# --- Scraper Endpoint ---




@app.post("/scrape", response_model=List[Union[schemas.ProductDetails, schemas.ErrorResponse]])
async def scrape_products(request: schemas.ScrapeRequest):
    # Note: We will protect this endpoint later
    if not request.urls:
        raise HTTPException(status_code=400, detail="URL list cannot be empty.")
    
    tasks = [scrape_url(str(url)) for url in request.urls]
    results = await asyncio.gather(*tasks)
    
    return results