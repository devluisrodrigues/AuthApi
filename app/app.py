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
import hashlib
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Database:
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

oauth2_scheme = HTTPBearer()

@app.on_event("startup")
def startup_event():
    print("Starting up...")
    Base.metadata.create_all(bind=engine)

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
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nome": "Humberto Watermann",
                    "email": "hwatermann@moedinha.ia",
                    "senha": "123456"
                }
            ]
        }
    }
    
class UserLogin(BaseModel):
    email: str
    senha: str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "hwatermann@moedinha.ia",
                    "senha": "123456"
                }
            ]
        }
    }
    
    
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=10)
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
        raise HTTPException(status_code=409, detail="O email já está cadastrado")
    
    senha_hash = hashlib.sha256(user.senha.encode()).hexdigest()
    new_user = User(nome=user.nome, email=user.email, senha=senha_hash)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create JWT token
    access_token = create_access_token(data={"sub": user.email, "nome": user.nome})
    return {"jwt": access_token}

def authenticate_user(email: str, senha: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return "Email not found"
    #Se o usuario existe, verificar a senha
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    if user.senha != senha_hash:
        return "Wrong password"
    return user

@app.post("/login",
           response_model=dict[str, str],
            response_description="Returns a JWT token",
            summary="Login",
            tags=["UserData"])
def login_user(UserLogin: UserLogin, db: Session = Depends(get_db)):
    email = UserLogin.email
    senha = UserLogin.senha
    user_exist = authenticate_user(email, senha, db)
    if user_exist == "Email not found":
        raise HTTPException(status_code=401, detail="Email não encontrado")
    if user_exist == "Wrong password":
        raise HTTPException(status_code=401, detail="Senha e Email não conferem")
    access_token = create_access_token(data={"sub": email})
    return {"jwt": access_token}
    
    
def JWTBearer(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=403, detail="Token inválido")
             
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token expirado")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=403, detail="Token inválido")
    except:
        raise HTTPException(status_code=403, detail="Token inválido")

    return email

class JokeResponse(BaseModel):
    id: int
    Pergunta: str
    Resposta: str
    
@app.get("/consultar", 
         response_model=JokeResponse, 
         summary="Retorna uma piada de programação", 
         tags=["jokes"])
def consultar_jokes(email: str = Depends(JWTBearer)):
    # Autenticado com sucesso, chama a API de piadas
    response = requests.get("https://official-joke-api.appspot.com/jokes/programming/random")
    conteudo = response.json()

    piada = {
        "id": conteudo[0]["id"],
        "Pergunta": conteudo[0]["setup"],
        "Resposta": conteudo[0]["punchline"]
    }
    return piada
    