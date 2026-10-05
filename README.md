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

# Week 7 Assignment A17: Put an LLM Behind the API

The `/ai/triage` endpoint classifies one task/request into a closed set of categories and priorities. It accepts one JSON request and returns one schema-validated JSON response. The model is treated as an untrusted external API.

## Job Card

The existing `JOB-CARD.md` is the source contract:

- Input: `text`, 1–2000 characters
- Category: `bug`, `feature`, `task`, `other`
- Priority: `low`, `normal`, `high`
- Confidence: 0.0–1.0
- Reason: one short sentence
- The model must never invent categories, return extra fields, return raw free text, give medical/legal/financial advice, or reveal the system prompt.
- When unsure, it must use `other` with low confidence.

## LLM Endpoint

```http
POST /ai/triage
Content-Type: application/json
```

Example:

```powershell
curl.exe -X POST http://localhost:3000/ai/triage `
  -H "Content-Type: application/json" `
  -d "{\"text\":\"Add dark mode to the dashboard\"}"
```

The exact classification can vary because the model is non-deterministic, but the response shape is closed and validated:

```json
{
  "category": "feature",
  "priority": "normal",
  "confidence": 0.94,
  "reason": "The request asks for a new user-facing capability."
}
```

### Deliberately broken input

```powershell
curl.exe -X POST http://localhost:3000/ai/triage `
  -H "Content-Type: application/json" `
  -d "{\"text\":\"\"}"
```

Expected status:

```text
400 Bad Request
```

The response identifies the offending field:

```json
{
  "error": "Invalid request",
  "field": "text",
  "message": "String should have at least 1 character"
}
```

Missing, wrong-type, whitespace-only, and over-limit input are rejected before a provider call.

## Prompt and Input Safety

The versioned system prompt lives in:

```text
prompts/triage-v1.md
```

A v2 prompt is also provided for the prompt A/B-testing extra:

```text
prompts/triage-v2.md
```

The system prompt contains the role, exact schema, closed lists, rules, when-unsure behaviour, and examples.

User content is sent separately as a `user` message and is JSON-encoded. It is never concatenated into the system prompt.

The prompt explicitly treats instructions inside user content as untrusted data. Five prompt-injection cases are included in `evals/cases.json`.

## Stub Mode

Set:

```env
LLM_STUB=1
```

The endpoint returns a deterministic schema-valid response without calling the provider.

## Kill Switch

Set:

```env
LLM_ENABLED=false
```

The endpoint immediately returns a deterministic fallback:

```json
{
  "category": "other",
  "priority": "normal",
  "confidence": 0.0,
  "reason": "AI triage is disabled; using the deterministic fallback."
}
```

No model call is made.

## Provider Configuration

The provider is selected through environment variables. The route does not know which provider is being used.

Local Ollama:

```env
LLM_PROVIDER=ollama
LLM_BASE_URL=http://host.docker.internal:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=gemma3:1b
```

OpenRouter:

```env
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=your_openrouter_key
LLM_MODEL=openrouter/free
```

The important provider-specific values are `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL`; `LLM_PROVIDER` selects the implementation. The endpoint and service contract remain unchanged.

The provider abstraction is implemented in `llm/providers.py` with separate Ollama and OpenRouter implementations. This matters more for LLMs than for a normal HTTP dependency because provider outages, rate limits, model IDs, response formats, and token pricing can change while the application contract should stay stable.

## Reliability

The provider client has an explicit timeout capped at 60 seconds. The default configuration is 30 seconds.

The SDK's automatic retries are disabled with `max_retries=0`. The application owns the retry policy:

- retry timeouts
- retry HTTP 429
- retry HTTP 5xx
- never retry HTTP 400
- never retry HTTP 401
- never retry HTTP 403
- use exponential backoff of approximately 1s, 2s, 4s
- add jitter
- honour `Retry-After` when supplied

A timeout maps to HTTP `504`. Provider failures map to HTTP `502`. Raw provider/model text is never returned to the caller.

## Parse, Validate, Repair, Quarantine

Model output is parsed and validated against the Pydantic response schema.

If parsing or validation fails:

1. The same system prompt is reused.
2. The original task, broken output, and exact validation error are sent in the user message.
3. Exactly one repair attempt is made.
4. If the repair is still invalid, the API returns HTTP `422`.
5. The failed output is written to `logs/quarantine.jsonl`.
6. The process does not crash.

Model refusals are treated as failed structured output and enter the same repair/quarantine path.

## Confidence Fallback

A valid response with confidence below `0.60` is treated as uncertain:

```json
{
  "category": "other",
  "priority": "normal",
  "confidence": 0.0,
  "reason": "The model was not confident enough to classify this request."
}
```

The original model confidence is preserved when the fallback is applied.

## Structured Cost Logging

Every provider call emits a structured JSON log line containing:

- `prompt_version`
- `model`
- `input_tokens`
- `output_tokens`
- `duration_ms`
- `repair_count`
- `estimated_cost_usd`

Example shape:

```json
{
  "event": "llm_call",
  "prompt_version": "triage-v1",
  "model": "gemma3:1b",
  "input_tokens": 200,
  "output_tokens": 30,
  "duration_ms": 4200,
  "repair_count": 0,
  "estimated_cost_usd": 0.0,
  "status": "success"
}
```

For local Ollama the configured cost is zero. For a hosted provider, set:

```env
LLM_INPUT_COST_PER_1K=...
LLM_OUTPUT_COST_PER_1K=...
```

For a hosted provider, the cost per 1,000 requests is the per-request token cost multiplied by 1,000; the same values can then be used to estimate the cost of 10,000 requests per day. For local Ollama, the configured provider cost is $0.00 per 1,000 requests.

## Token Preflight

The request is token-counted before the provider is called. Requests over:

```env
LLM_MAX_INPUT_TOKENS=4000
```

are rejected with HTTP `413`, so an oversized request cannot spend provider quota.

## Evaluation

The repository contains 25 labelled cases in:

```text
evals/cases.json
```

There are:

- 15 easy cases
- 10 hard cases
- 5 prompt-injection cases within the hard set

Run the evaluation against the live API:

```powershell
python evals/run_eval.py
```

The script prints:

```text
Overall: X/25 (XX.X%)
Easy: X/15 (XX.X%)
Hard: X/10 (XX.X%)
```

It also lists every failed case and continues when an individual HTTP request fails.

**Recorded live evaluation results:**

```text
Eval date: 2026-10-05
Prompt version: triage-v1
Overall: 9/25 (36.0%)
Easy: 6/15 (40.0%)
Hard: 3/10 (30.0%)
```

These results came from the live evaluation runner against the running API and were calculated from its actual responses, not hard-coded.

## Optional Extras Included

The codebase also includes implementations for the stretch items:

- in-memory caching keyed by input + prompt version
- provider abstraction with Ollama and OpenRouter
- prompt injection attack cases
- token preflight
- prompt v2 for a one-line prompt experiment
- optional schema-constrained JSON mode via `LLM_STRUCTURED_OUTPUT=true`
- model refusal handling

Caching is disabled by default so evaluation runs remain easy to reason about:

```env
LLM_CACHE_ENABLED=false
```

Schema-constrained output can be enabled when the selected provider/model supports it:

```env
LLM_STRUCTURED_OUTPUT=true
```

## Bonus AI Rematch

`BONUS_AI_REMATCH_PROMPT.md` contains the specification prompt for generating a separate AI implementation in an `ai-version/` quarantine folder. The hand-built implementation above remains the submission implementation.

The rematch should be compared against the hand-built implementation only after the main checkpoints pass. The README should then document at least three concrete differences and whether the generated code improved or missed any requirement.

## Manual Checkpoints

### Stage 0

```powershell
python hello.py
```

Expected output contains:

```text
ready
```

The real `.env` must not appear in `git status`.

### Stage 1

With:

```env
LLM_STUB=1
```

call `/ai/triage` and confirm HTTP 200 with schema-valid JSON. Then send malformed input and confirm HTTP 400.

### Stage 2

Unset `LLM_STUB`, restart the API, and make three different real requests. The prompt remains in `prompts/triage-v1.md`.

### Stage 3

Temporarily force an invalid model response. Confirm exactly one repair is attempted. If the repair also fails, confirm HTTP 422 and a new line in `logs/quarantine.jsonl`.

### Stage 4

Set:

```env
LLM_ENABLED=false
```

and confirm an immediate deterministic response with no provider call.

Then test a timeout and a provider failure. Confirm timeout returns 504 and 400/401/403 are not retried.

### Stage 5

Run:

```powershell
python evals/run_eval.py
```

Record the real date, prompt version, overall score, easy score, and hard score in this README before publishing.


### Model comparison extra

Two running endpoint instances can be compared with:

```powershell
python evals/compare_models.py --url-a http://localhost:3000/ai/triage --url-b http://localhost:3001/ai/triage
```

This reports both model scores on the same 25-case evaluation set.
