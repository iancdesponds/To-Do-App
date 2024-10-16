# Usar a imagem oficial do Python
FROM python:3.11-slim

# Definir o diretório de trabalho
WORKDIR /app

# Copiar apenas o arquivo de dependências primeiro
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante dos arquivos do projeto para o contêiner
COPY . /app

# Expor a porta que o FastAPI irá rodar
EXPOSE 8000

# Comando para rodar o FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]