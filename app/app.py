from fastapi import FastAPI, HTTPException, Depends
from typing import Union
import requests
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Database:
#para teste local localhost, senha admin@2024, host:localhost, porta:5432, database:fastapi
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

@app.on_event("startup")
def startup_event():
    print("Starting up...")
    Base.metadata.create_all(bind=engine)

@app.get("/jokes/programming",
            response_model=Union[dict],
            response_description="Returns a dictionary with a programming joke",
            summary="Returns a programming joke",
            tags=["jokes"])
def programming_jokes():
    response = requests.get("https://official-joke-api.appspot.com/jokes/programming/random")
    conteudo = response.json()
    piada = dict()
    piada["id"] = conteudo[0]["id"]
    piada["Pergunta"] = conteudo[0]["setup"]
    piada["Resposta"] = conteudo[0]["punchline"]
    return piada

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha = Column(String)
    
class UserCreate(BaseModel):
    nome: str
    email: str
    senha: str
    
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt  
    
@app.post("/registrar",
           response_model=dict[str, str],
            response_description="Returns a JWT token",
            summary="Register a new user",
            tags=["UserData"])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    user_exists = db.query(User).filter(User.email == user.email).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = User(nome=user.nome, email=user.email, senha=user.senha)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create JWT token
    access_token = create_access_token(data={"sub": user.email, "nome": user.nome})
    return {"access_token": access_token, "token_type": "bearer"}