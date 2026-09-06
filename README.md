# Task API

A simple FastAPI task management API using PostgreSQL for persistent storage. It supports CRUD operations, SQL-based search, filtering, sorting, statistics, and timestamps.

## What this is

This project is a small task management API built with FastAPI and PostgreSQL. It can create, retrieve, update, and delete tasks. Search, filtering, alphabetical sorting, and statistics are performed directly in PostgreSQL.

The complete application stack runs with one Docker Compose command.

## Features

- Create, retrieve, update, and delete tasks
- Persistent PostgreSQL storage
- Search tasks by title
- Filter tasks by completion status
- Alphabetical sorting
- Task statistics
- Creation and update timestamps
- Health check endpoint
- Interactive Swagger documentation at `/docs`
- One-command Docker Compose startup
- PostgreSQL persistence through a Docker volume

## Tech Stack

- Python
- FastAPI
- Psycopg
- PostgreSQL
- Docker
- Docker Compose
- Redis

## Project Structure

```text
main.py
routes.py
schemas.py
database.py
Dockerfile
compose.yaml
.env.example
.gitignore
README.md
screenshots/
```

- `main.py` — FastAPI app and startup/database initialization.
- `routes.py` — API routes and database operations.
- `schemas.py` — Pydantic request/response models.
- `database.py` — PostgreSQL connection and initialization.
- `Dockerfile` — API container definition.
- `compose.yaml` — API and PostgreSQL services.
- `.env.example` — required environment variable template.
- `.env` — local environment configuration; not committed.

## Database

The application uses **PostgreSQL**.

The `tasks` table is created automatically when the application starts. Three sample tasks are inserted only when the table is empty.

### Tasks Table

| Field | Type | Description |
|---|---|---|
| `id` | SERIAL | Automatically generated primary key |
| `title` | TEXT | Task title |
| `done` | BOOLEAN | Completion status |
| `created_at` | TEXT | Creation timestamp |
| `updated_at` | TEXT | Last update timestamp |

## Environment Variables

The application uses `DATABASE_URL`.

Copy `.env.example` to `.env` and set the required value:

```env
DATABASE_URL=postgres://postgres:YOUR_PASSWORD@localhost:5433/tasks
```

The `.env` file is git-ignored. `.env.example` is committed.

Inside Docker Compose, the API connects to PostgreSQL using the service name `db`, not `localhost`.

## Run Everything With One Command

After cloning:

```bash
cp .env.example .env
docker compose up
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up
```

The API is available at:

```text
http://localhost:3000
```

Swagger UI:

```text
http://localhost:3000/docs
```

No manual PostgreSQL setup is required.

## API Endpoints

| Method | Endpoint | Description | Success |
|---|---|---|---|
| GET | `/` | API information | 200 |
| GET | `/health` | Health check | 200 |
| GET | `/tasks` | Get all tasks | 200 |
| GET | `/tasks/{task_id}` | Get one task | 200 |
| POST | `/tasks` | Create a task | 201 |
| PUT | `/tasks/{task_id}` | Update a task | 200 |
| DELETE | `/tasks/{task_id}` | Delete a task | 204 |
| GET | `/tasks?search=...` | Search tasks | 200 |
| GET | `/tasks?done=true/false` | Filter tasks | 200 |
| GET | `/stats` | Task statistics | 200 |

Unknown task IDs return `404` with a task-not-found error.

## Example `curl -i`

```bash
curl -i http://localhost:3000/tasks
```

Expected result:

```text
HTTP/1.1 200 OK
```

followed by the task rows returned from PostgreSQL.

## Other Requests

### Get one task

```bash
curl -i http://localhost:3000/tasks/1
```

### Create a task

```bash
curl -i -X POST "http://localhost:3000/tasks" ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Learn FastAPI\"}"
```

### Update a task

```bash
curl -i -X PUT "http://localhost:3000/tasks/1" ^
  -H "Content-Type: application/json" ^
  -d "{\"done\":true}"
```

### Delete a task

```bash
curl -i -X DELETE "http://localhost:3000/tasks/1"
```

### Search

```bash
curl -i "http://localhost:3000/tasks?search=home"
```

### Filter

```bash
curl -i "http://localhost:3000/tasks?done=false"
```

### Statistics

```bash
curl -i http://localhost:3000/stats
```

## SQL Search, Filtering, and Sorting

Search uses a parameterized PostgreSQL query with `ILIKE`:

```http
GET /tasks?search=home
```

Filtering:

```http
GET /tasks?done=true
GET /tasks?done=false
```

Sorting is performed by PostgreSQL:

```sql
ORDER BY title
```

Search and filtering can be combined:

```http
GET /tasks?done=false&search=do
```

## Task Statistics

**GET `/stats`**

Example:

```json
{
  "total": 3,
  "completed": 1,
  "pending": 2
}
```

Statistics are calculated using SQL `COUNT(*)` queries.

## Timestamps

Each task contains:

```text
created_at
updated_at
```

Both are set when a task is created. On update, only `updated_at` changes.

## PostgreSQL Database Check

List the tables:

```bash
docker exec -it assignment1-db-1 psql -U postgres -d tasks -c "\dt"
```

View the stored tasks:

```bash
docker exec -it assignment1-db-1 psql -U postgres -d tasks -c "SELECT * FROM tasks;"
```

## Redis

Redis is included in the Docker Compose stack as a supporting service.

The API connects to Redis using the Docker Compose service name `redis` and sends a `PING` command during startup. 

A successful connection returns:

```text
PONG
```

Redis can also be checked directly with:

```bash
docker exec assignment1-redis-1 redis-cli ping
```

Expected output:

```text
PONG
```


### Database Screenshot

![PostgreSQL Database](screenshots/postgresql-database.png)

The screenshot should show the PostgreSQL `tasks` table and its stored task data.

## Persistence Check

Create a task, then restart the complete stack:

```bash
docker compose down
docker compose up
```

The task remains because PostgreSQL data is stored in the `taskdata` Docker volume.

## Clean Clone / Stranger Run

A stranger should be able to:

```bash
cp .env.example .env
docker compose up
```

Then:

```bash
curl -i http://localhost:3000/tasks
```

The API and PostgreSQL database start together, the `tasks` table is created automatically, and the three seed tasks appear when the database is empty.

No manual database setup is required.

## Security

- `.env` is excluded from Git.
- `.env.example` contains placeholder credentials.
- Database credentials are supplied through environment variables.
- SQL values are passed using parameterized queries.
- A real database password must never be committed.

## Screenshots

### Swagger UI

![Swagger UI](screenshots/swagger-ui.png)

### GET /tasks Response

![GET /tasks Response](screenshots/task-api-example.png)

### POST /tasks Request

![POST /tasks Request](screenshots/post-task-request.png)

### PostgreSQL Database

![PostgreSQL Database](screenshots/postgres-database.png)

## Notes

- PostgreSQL runs as the `db` service in Docker Compose.
- The API runs as the `api` service.
- Inside the Compose network, the database hostname is `db`.
- PostgreSQL data is persisted in the `taskdata` Docker volume.
- Three sample tasks are inserted only when the table is empty.
- Search and filtering are performed in SQL.
- Sorting uses SQL `ORDER BY`.
- Statistics use SQL `COUNT(*)`.
- User-provided SQL values use parameterized queries.

## Multi-Stage Docker Build

The Dockerfile uses a multi-stage build with separate builder and runtime stages.

The builder stage installs the Python dependencies, while the final runtime stage copies only the installed dependencies and application files.

### Image Size Comparison

| Version | Disk Usage | Content Size |
|---|---:|---:|
| Before multi-stage build | 335 MB | 77.4 MB |
| After multi-stage build | 320 MB | 73.7 MB |

The multi-stage build reduced the Docker image disk usage by approximately 15 MB.

## Future Improvements

- Database migrations
- Pagination
- Authentication
- More advanced filtering
- Additional task fields
# Authentication (Supabase Auth)

This project also includes the authentication requirements from the FlyRank Backend Track Week 2 Assignment A4: **Auth · Login & protect**.

Authentication is handled by **Supabase Auth**. The application does not store passwords or implement password hashing itself. Supabase manages user accounts, passwords, and JWT access tokens. The backend verifies access tokens through Supabase before allowing protected routes.

## Authentication Features

- User signup with Supabase Auth
- User login with email and password
- JWT access-token authentication
- Bearer-token verification using Supabase
- Reusable FastAPI authentication dependency
- Protected profile endpoint
- Protected dashboard endpoint
- Protected logout endpoint
- Public information endpoint
- Swagger UI Bearer authentication with the `Authorize` padlock

## Authentication Environment Variables

In addition to `DATABASE_URL`, the application uses these Supabase environment variables:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
PORT=3000
```

The `SUPABASE_KEY` must be the Supabase **anon/public key**. Never use or commit the Supabase `service_role` key.

The real `.env` file is git-ignored. A `.env.example` file is committed with placeholder values so another developer can configure their own environment without receiving any secrets.

A complete `.env.example` should contain:

```env
DATABASE_URL=your_database_url
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
PORT=3000
```

## Authentication API Endpoints

| Method | Endpoint | Authentication | Description | Success |
|---|---|---|---|---|
| POST | `/auth/signup` | None | Create a new Supabase user account | 201 |
| POST | `/auth/login` | None | Authenticate and return access and refresh tokens | 200 |
| POST | `/auth/logout` | Bearer token | Sign out the authenticated user | 204 |
| GET | `/protected/profile` | Bearer token | Return safe metadata for the authenticated user | 200 |
| GET | `/protected/dashboard` | Bearer token | Return protected dashboard information | 200 |
| GET | `/public/info` | None | Return public information | 200 |

## Authentication Flow

The authentication flow is:

```text
Sign up / Login
      ↓
Supabase Auth
      ↓
Access token (JWT)
      ↓
Client sends:
Authorization: Bearer <token>
      ↓
FastAPI authentication dependency
      ↓
Supabase token verification
      ↓
Protected route
```

## Signup

**POST `/auth/signup`**

Request:

```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

A successful signup returns HTTP `201` with the created user's ID and email.

Missing email or password returns HTTP `400`.

## Login

**POST `/auth/login`**

Request:

```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

A successful login returns HTTP `200` with:

- `access_token`
- `refresh_token`

Invalid credentials return HTTP `401`:

```json
{
  "error": "Invalid login credentials"
}
```

## Protected Profile

**GET `/protected/profile`**

Send the access token using:

```http
Authorization: Bearer <access_token>
```

A valid token returns the authenticated user's safe metadata, including:

- `id`
- `email`
- `created_at`

Missing or malformed authentication returns HTTP `401`:

```json
{
  "error": "Access token required"
}
```

An invalid or expired token returns HTTP `401`:

```json
{
  "error": "Invalid or expired token"
}
```

## Protected Dashboard

**GET `/protected/dashboard`**

This route uses the same reusable authentication dependency as `/protected/profile`.

A valid token returns HTTP `200`:

```json
{
  "message": "Welcome to your protected dashboard",
  "user_id": "..."
}
```

## Logout

**POST `/auth/logout`**

This endpoint requires a valid Bearer token and returns HTTP `204` on successful sign-out.

## Public Information

**GET `/public/info`**

This endpoint does not require authentication.

Successful response:

```json
{
  "message": "Welcome stranger! This info is public."
}
```

## Authentication Testing With curl

### Signup

```bash
curl -i -X POST "http://localhost:3000/auth/signup" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"user@example.com\",\"password\":\"your-password\"}"
```

### Login

```bash
curl -i -X POST "http://localhost:3000/auth/login" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"user@example.com\",\"password\":\"your-password\"}"
```

Copy the `access_token` from the login response.

### Protected Profile

```bash
curl -i "http://localhost:3000/protected/profile" ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Protected Dashboard

```bash
curl -i "http://localhost:3000/protected/dashboard" ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Public Information

```bash
curl -i "http://localhost:3000/public/info"
```

### Test Missing Authentication

```bash
curl -i "http://localhost:3000/protected/profile"
```

Expected status:

```text
401 Unauthorized
```

### Test a Tampered Token

Change one character in the access token and send it again:

```bash
curl -i "http://localhost:3000/protected/profile" ^
  -H "Authorization: Bearer TAMPERED_ACCESS_TOKEN"
```

Expected status:

```text
401 Unauthorized
```

with:

```json
{
  "error": "Invalid or expired token"
}
```

## Swagger UI Authentication

FastAPI provides interactive Swagger documentation at:

```text
http://localhost:3000/docs
```

The protected authentication routes use FastAPI's HTTP Bearer security scheme.

In Swagger UI:

1. Open `/docs`.
2. Click the **Authorize** padlock.
3. Paste the access token from `/auth/login`.
4. Do not manually add the `Bearer ` prefix when Swagger asks for the bearer token.
5. Click **Authorize**.
6. Use **Try it out** on `/protected/profile` or `/protected/dashboard`.

The protected routes should display the lock icon and Swagger should send the token in the `Authorization: Bearer <token>` header.

## Authentication Security

- Supabase manages passwords and authentication.
- The backend does not store user passwords.
- Only the Supabase anon/public key is used by the application.
- The Supabase `service_role` key must never be used here.
- `.env` is excluded from Git.
- `.env.example` contains placeholders only.
- Access tokens are sent using the standard `Authorization: Bearer <token>` header.
- Protected routes verify the token with Supabase before returning private user information.
- Invalid, expired, missing, or malformed tokens are rejected with HTTP `401`.

## Assignment Stage Commits

The authentication work was completed stage by stage as required:

```text
Stage 0: setup server and supabase client
Stage 1: signup and login routes working
Stage 2: public route and unverified protected route
Stage 3: profile route token verification
Stage 4: auth middleware and logout endpoint
Stage 5: Swagger UI documentation with bearer auth
Stage 6: publish to GitHub and write README
```

## GitHub / Clean Setup

Before publishing the repository:

- Confirm `.env` is listed in `.gitignore`.
- Confirm `.env` has never been committed.
- Commit `.env.example` with placeholder values.
- Do not place Supabase keys or database passwords in source code.
- Push the stage commits to the public GitHub repository.

A fresh clone should be able to create its own `.env`, run Docker Compose, configure Supabase credentials, and use the authenticated API without access to the original developer's secrets.
