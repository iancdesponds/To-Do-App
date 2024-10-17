from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, constr
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio
from redis import Redis
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
import pytz
import bleach
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Definir o fuso horário BRT (Horário de Brasília)
BRT = pytz.timezone("America/Sao_Paulo")

# Inicializando FastAPI
app = FastAPI()

# Configurando o CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # URL do frontend
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexão com MongoDB
MONGO_DETAILS = os.getenv("MONGO_DETAILS")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS) # Cliente do MongoDB
db = client.todo_app # Banco de dados
task_collection = db.get_collection("tasks") # Coleção de tarefas
user_collection = db.get_collection("users")  # Coleção de usuários

# Conexão com Redis (para cache)
redis_client = Redis(host="redis-to-do", port=6379, db=0)

# Configurações de segurança para senha e JWT
SECRET_KEY = os.getenv("SECRET_KEY") # Chave secreta para assinar o token JWT
ALGORITHM = "HS256" # Algoritmo de criptografia para o token JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 600 # Tempo de expiração do token JWT
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Contexto de criptografia para a senha

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # URL para obter o token JWT

# Função de sanitização
def sanitize_input(input_string: str) -> str:
    return bleach.clean(input_string)

# Modelos de dados
class Task(BaseModel): # Modelo de tarefa
    title: str = Field(min_length=1, max_length=100) # Título deve ter de 1 a 100 caracteres
    description: Optional[str] = None
    status: str = "pendente" # O status padrão é "pendente"
    id: Optional[str] = None

    class Config: # Configuração para converter o objeto Pydantic para dicionário
        orm_mode = True

class User(BaseModel): # Modelo de usuário
    username: str
    password: str

class Token(BaseModel): # Modelo de token JWT
    access_token: str
    token_type: str

class TokenData(BaseModel): # Modelo de dados do token JWT
    username: Optional[str] = None

# Funções auxiliares para autenticação
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Funções de autenticação e autorização
async def get_user(username: str): # Função para buscar um usuário no banco de dados
    user = await user_collection.find_one({"username": username})
    if user:
        return user
    return None

async def authenticate_user(username: str, password: str): # Função para autenticar um usuário
    user = await get_user(username)
    if not user or not verify_password(password, user["password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None): # Função para criar um token JWT
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(BRT) + expires_delta
    else:
        expire = datetime.now(BRT) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)): # Função para obter o usuário atual
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Funções auxiliares para cache

# Cacheando uma tarefa no Redis
async def cache_task(task_id, task_data):
    redis_client.set(task_id, task_data)

# Recuperando uma tarefa do Redis
async def get_cached_task(task_id):
    task_data = redis_client.get(task_id)
    if task_data:
        return task_data
    return None

# Rotas de autenticação e criação de usuários

# Rota para cadastrar um novo usuário
@app.post("/register/")
async def register(user: User):
    if await get_user(user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = {"username": sanitize_input(user.username), "password": hashed_password}
    await user_collection.insert_one(new_user)
    return {"message": "User created successfully"}

# Rota para fazer login e gerar o token JWT
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(sanitize_input(form_data.username), form_data.password)
    if not user:
        raise HTTPException(
            status_code=401, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Rota para fazer logout
@app.post("/logout")
async def logout():
    return {"message": "Logout successful"}

# Rotas de tarefas, protegidas com autenticação JWT

# Rota para listar todas as tarefas
@app.get("/tasks/", response_model=List[Task])
async def get_tasks(current_user: dict = Depends(get_current_user)):
    tasks = await task_collection.find().to_list(100)
    for task in tasks:
        task["id"] = str(task["_id"])
    return tasks

# Rota para criar uma nova tarefa
@app.post("/tasks/", response_model=Task)
async def create_task(task: Task, current_user: dict = Depends(get_current_user)):
    if not task.title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    # Sanitiza as entradas de título e descrição
    task.title = sanitize_input(task.title)
    if task.description:
        task.description = sanitize_input(task.description)
    
    task_dict = task.model_dump() # Converter o objeto Pydantic para dicionário
    
    if "id" in task_dict: # Remover o campo `id` do dicionário caso exista, para evitar erros
        del task_dict["id"]

    new_task = await task_collection.insert_one(task_dict)
    created_task = await task_collection.find_one({"_id": new_task.inserted_id})
    
    return created_task

# Rota para atualizar o status de uma tarefa - troca o status de "pendente" para "concluída" e vice-versa
@app.put("/tasks/{task_id}")
async def update_task_status(task_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    task = await task_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Alternar o status da tarefa
    new_status = "completa" if task["status"] == "pendente" else "pendente"

    # Atualizar o status da tarefa no banco de dados
    updated_task = await task_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": new_status}})
    
    if updated_task.modified_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task status updated successfully", "new_status": new_status}

# Rota para deletar uma tarefa
@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    
    deleted_task = await task_collection.delete_one({"_id": ObjectId(task_id)})
    
    if deleted_task.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task deleted successfully"}
