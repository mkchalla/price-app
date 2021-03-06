from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import inspect
from typing import Optional
from jose import JWTError, jwt

from passlib.context import CryptContext

from . import models, schemas

SECRET_KEY = "872503a203f21d07cb356c7e1837f1e24701bea3761357624ffe0af6782cb860"
ALGORITHM = "HS256"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_user(db: Session, user: models.User):
    db_user = models.User(username=user.username,hashed_password=get_password_hash(user.password), email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)    
    return schemas.User(username=user.username)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def get_product(db: Session, product_id: int):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    return product


def create_product(db: Session, product: schemas.ProductBase, image_url:str):
    db_product = models.Product(name=product.name,description=product.description,image=image_url)
    db.add(db_product)
    db.commit()
    db.refresh(db_product) 
    return db.query(models.Product).filter(models.Product.id == db_product.id).first()