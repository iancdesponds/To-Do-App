# To-Do List API - FastAPI Backend

Este projeto é uma API para gerenciamento de tarefas (**To-Do List**) desenvolvida em **Python** com o framework **FastAPI**. A API oferece endpoints para criar, listar, atualizar e excluir tarefas, além de suporte à autenticação com **JWT**. O projeto também utiliza **MongoDB** para armazenamento persistente e **Redis** para cache.

## Funcionalidades

- **CRUD de Tarefas**: Criação, listagem, atualização e exclusão de tarefas.
- **Autenticação com JWT**: Apenas usuários autenticados podem manipular as tarefas.
- **Cache com Redis**: As tarefas são armazenadas em cache para otimizar a performance.
- **Validação de Dados**: As tarefas têm validações de dados como o limite de caracteres no título.
- **Sanitização de Entradas**: Para evitar injeção de código e garantir a segurança das entradas.

## Tecnologias Utilizadas

### Backend
- **Python**: Linguagem de programação principal.
- **FastAPI**: Framework web para construção de APIs rápidas e modernas.
- **MongoDB**: Banco de dados NoSQL utilizado para persistir as tarefas.
- **Redis**: Utilizado para cachear tarefas e melhorar a performance.
- **JWT (JSON Web Token)**: Autenticação baseada em tokens para proteger os endpoints.
- **Motor**: Driver assíncrono para integração com MongoDB.
- **Pydantic**: Validação de dados para os modelos da aplicação.
- **Passlib**: Biblioteca para hashing de senhas.
- **Bleach**: Utilizado para sanitizar as entradas do usuário.

### Ferramentas de Desenvolvimento
- **Docker**: A aplicação é preparada para ser executada em contêineres Docker.
- **Docker Compose**: Para orquestrar o MongoDB, Redis e o servidor FastAPI.

## Como Executar Localmente

### Pré-requisitos

- **Docker** instalado na máquina.
- Um arquivo `.env` com as seguintes variáveis configuradas:
  ```
  MONGO_DETAILS=mongodb://mongo-to-do:27017
  SECRET_KEY=your_secret_key
  ```

### Passos para executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio-backend.git
   cd seu-repositorio-backend
   ```

2. Construa e inicie os contêineres com Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Acesse a API em `http://localhost:8000`.

4. Documentação interativa da API (Swagger):
   - Após iniciar o projeto, acesse `http://localhost:8000/docs` para visualizar a documentação interativa da API gerada pelo Swagger.

### Endpoints Principais

- **Autenticação e Registro de Usuário:**
  - `POST /register`: Cria um novo usuário.
  - `POST /token`: Autentica um usuário e retorna o token JWT.
  
- **Gerenciamento de Tarefas:**
  - `GET /tasks/`: Lista todas as tarefas (necessário autenticação JWT).
  - `POST /tasks/`: Cria uma nova tarefa (necessário autenticação JWT).
  - `PUT /tasks/{task_id}`: Atualiza o status de uma tarefa (necessário autenticação JWT).
  - `DELETE /tasks/{task_id}`: Exclui uma tarefa (necessário autenticação JWT).

## O que está faltando para o Deploy na AWS

Para fazer o deploy na **AWS**, aqui estão os passos e o que está faltando:

### 1. **Configurar AWS para Hospedar o Back-end**
   - Utilize o **AWS Elastic Beanstalk** ou o **Amazon ECS (Elastic Container Service)** para hospedar sua aplicação Docker.
   - Alternativamente, você pode usar o **AWS EC2** para rodar o Docker manualmente.
   - **Passos gerais**:
     1. Crie uma instância EC2 ou um cluster ECS.
     2. Configure o **Docker** na instância ou no cluster.
     3. Faça o deploy da aplicação a partir do **Docker Compose**.

### 2. **Banco de Dados MongoDB**
   - Atualmente, o MongoDB está sendo executado localmente via Docker Compose.
   - **Sugestão**: Utilize o **MongoDB Atlas** (MongoDB em nuvem) ou configure um **Amazon DocumentDB** (compatível com MongoDB) para o deploy em produção.

### 3. **Redis**
   - O Redis também está sendo executado localmente via Docker.
   - **Sugestão**: Utilize o **Amazon ElastiCache** para Redis em produção.

### 4. **Configurar Certificado SSL (HTTPS)**
   - Para garantir que o tráfego seja seguro, configure o **Amazon Certificate Manager (ACM)** para gerenciar certificados SSL.
   - O AWS Load Balancer pode ser usado para fornecer HTTPS para a aplicação.

### 5. **Configurar Variáveis de Ambiente na AWS**
   - Configure as variáveis de ambiente necessárias (como `SECRET_KEY` e `MONGO_DETAILS`) no ambiente AWS onde o deploy será feito (Elastic Beanstalk ou ECS).

### 6. **Logging e Monitoramento**
   - Configure o **CloudWatch** para monitorar os logs da aplicação e detectar problemas.

## Melhorias Futuras

- **Testes automatizados**: Adicionar testes unitários e de integração com `pytest`.
- **Monitoramento de performance**: Integrar ferramentas como **Prometheus** ou **Grafana** para monitorar o desempenho da aplicação.
- **Melhoria da segurança JWT**: Implementar renovação de tokens e revogação de tokens.

---

Com esse **README**, os desenvolvedores e outros interessados poderão entender melhor o que a aplicação faz, como configurá-la localmente, quais tecnologias ela usa e o que falta para o deploy na AWS.