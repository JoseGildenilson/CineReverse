# 🎬 CineReserve API

API RESTful para o sistema de reservas do **Cinépolis Natal**.

## Tech Stack

- **Python 3.12** + **FastAPI**
- **PostgreSQL** (SQLAlchemy async + Alembic)
- **Redis** (locks distribuídos + cache de leitura)
- **JWT** (autenticação via `python-jose`)
- **Poetry** (gerenciamento de dependências)
- **Docker** + **Docker Compose**

## Setup com Docker

```bash
# Clone o repositório
git clone https://github.com/JoseGildenilson/CineReverse.git
cd CineReverse

# Crie o arquivo .env a partir do exemplo
cp .env.example .env

# Suba todos os serviços
docker compose up --build
```

A API estará disponível em `http://localhost:8000`.

Documentação Swagger: `http://localhost:8000/docs`

## Setup Local (desenvolvimento)

```bash
# Instale as dependências
poetry install

# Suba o PostgreSQL e Redis via Docker
docker compose up cinereserve-db cinereserve-redis -d

# Crie o .env a partir do exemplo
cp .env.example .env
# Edite o .env trocando os hosts para localhost:
#   DATABASE_URL=postgresql+asyncpg://cine_user:cine_pass@localhost:5432/cinereserve
#   REDIS_URL=redis://localhost:6379/0

# Rode as migrações
poetry run alembic upgrade head

# Inicie o servidor
poetry run uvicorn app.main:app --reload
```

## Endpoints

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/auth/register` | Cadastro de usuário | ❌ |
| POST | `/auth/login` | Login (retorna JWT) | ❌ |
| GET | `/auth/me` | Dados do usuário logado | ✅ |
| GET | `/movies/` | Listar filmes (paginado) | ❌ |
| GET | `/movies/{id}` | Detalhes de um filme | ❌ |
| POST | `/movies/` | Criar filme | ✅ |
| GET | `/sessions/` | Listar sessões (paginado) | ❌ |
| GET | `/sessions/movie/{id}` | Sessões de um filme (paginado) | ❌ |
| GET | `/sessions/{id}` | Detalhes de uma sessão | ❌ |
| POST | `/sessions/` | Criar sessão | ✅ |
| GET | `/sessions/{id}/seats` | Mapa de assentos | ❌ |
| POST | `/reservations/` | Reservar assento (10min lock) | ✅ |
| DELETE | `/reservations/{session_id}/{seat_id}` | Liberar reserva | ✅ |
| POST | `/tickets/checkout` | Confirmar compra | ✅ |
| GET | `/tickets/me` | Meus ingressos (paginado) | ✅ |
| GET | `/rooms/` | Listar salas | ❌ |
| POST | `/rooms/` | Criar sala | ✅ |

## Testes

```bash
poetry run pytest tests/ -v
```

## Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| `DATABASE_URL` | URL do PostgreSQL |
| `REDIS_URL` | URL do Redis |
| `SECRET_KEY` | Chave secreta para JWT |
| `DEBUG` | Modo debug (True/False) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tempo de expiração do token |
