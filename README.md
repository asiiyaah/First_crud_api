# Task API

A simple FastAPI-based task management API with CRUD endpoints for tasks, SQLite database storage, and SQL-based search, filtering, sorting, statistics, and timestamps.

## Introduction

FastAPI is a Python framework used to build APIs quickly and easily. It is beginner-friendly and helps you create web services with less code. It also provides automatic validation and built-in API documentation, which makes testing an API easier.

This project is a small task management API. You can use it to create tasks, view all tasks, view one task by ID, update a task, or delete a task. The project initially used an in-memory list for storing tasks and was then connected to a SQLite database so task data persists after the server is restarted.

The database is also used to perform searching, filtering, alphabetical sorting, and statistics directly using SQL.

## Features

- Create, retrieve, update, and delete tasks
- Persistent SQLite database storage
- Search tasks by title using SQL
- Filter tasks by completion status using SQL
- Sort tasks alphabetically using SQL
- View task statistics using SQL
- Track task creation and update timestamps
- Built-in health check endpoint
- Interactive API documentation at `/docs`

## Project Structure

```text
main.py
routes.py
schemas.py
database.py
tasks.db
README.md
screenshots/
```

- `main.py` contains the FastAPI app instance, root/health endpoints, database initialization, and router registration.
- `routes.py` defines task-related API routes and database operations.
- `schemas.py` contains Pydantic request and response models.
- `database.py` contains the SQLite connection and initialization logic.
- `tasks.db` is the local SQLite database file.
- `README.md` contains project documentation.
- `screenshots/` contains screenshots used in this README.

## Database

The application uses **SQLite** to store tasks instead of an in-memory Python list.

The database file is:

```text
tasks.db
```

It is created automatically when the application starts.

### Tasks Table

| Field | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key generated automatically by SQLite |
| `title` | TEXT | Task title |
| `done` | INTEGER | Completion status (`0` = false, `1` = true) |
| `created_at` | TEXT | Time when the task was created |
| `updated_at` | TEXT | Time when the task was last updated |

The task ID is generated automatically using:

```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
```

Three sample tasks are inserted only when the table is empty, preventing duplicate sample tasks on server restart.

## API Endpoints

### 1. Root Endpoint

**GET `/`**

Returns basic API information.

```json
{
  "name": "Task API",
  "version": "1.0",
  "endpoints": ["/tasks"]
}
```

### 2. Health Check

**GET `/health`**

```json
{
  "status": "ok"
}
```

### 3. Get All Tasks

**GET `/tasks`**

Returns all tasks from SQLite, sorted alphabetically by title.

### 4. Get One Task

**GET `/tasks/{task_id}`**

Example:

```http
GET /tasks/1
```

A missing task returns `404 Not Found`.

### 5. Create a Task

**POST `/tasks`**

Status code: `201 Created`

Request:

```json
{
  "title": "Learn FastAPI"
}
```

When a task is created, both timestamps are set to the current time.

### 6. Update a Task

**PUT `/tasks/{task_id}`**

Request:

```json
{
  "title": "Learn FastAPI thoroughly",
  "done": true
}
```

A single field can also be updated:

```json
{
  "done": true
}
```

`created_at` remains unchanged while `updated_at` is changed to the current time.

An empty update body returns `400 Bad Request`. A missing task returns `404 Not Found`.

### 7. Delete a Task

**DELETE `/tasks/{task_id}`**

Successful deletion returns `204 No Content`.

A missing task returns `404 Not Found`.

## SQL-Based Extras

### Search Tasks

```http
GET /tasks?search=milk
```

The database uses:

```sql
WHERE title LIKE ?
```

Partial matches are supported.

### Filter by Status

Completed:

```http
GET /tasks?done=true
```

Incomplete:

```http
GET /tasks?done=false
```

The database uses:

```sql
WHERE done = ?
```

Python booleans are converted to SQLite values: `true -> 1` and `false -> 0`.

### Alphabetical Sorting

Tasks are sorted by title using:

```sql
ORDER BY title
```

The database performs the sorting instead of Python.

Filtering and searching can also be combined with sorting:

```http
GET /tasks?done=false&search=do
```

### Task Statistics

**GET `/stats`**

Example response:

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

When a task is created, both timestamps are set to the current time.

When a task is updated, only `updated_at` changes. `created_at` continues to represent the original creation time.

Adding `created_at` and `updated_at` required changing the structure of the existing database table, which made the change feel more involved than simply modifying Python code. Having to recreate the table for this small change made it clear why database migrations are useful for safely managing changes to a table's shape.

## Example Requests

### Get all tasks

```bash
curl http://127.0.0.1:8000/tasks
```

### Get one task

```bash
curl http://127.0.0.1:8000/tasks/1
```

### Create a task

```bash
curl -X POST "http://127.0.0.1:8000/tasks" ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Learn FastAPI\"}"
```

### Update a task

```bash
curl -X PUT "http://127.0.0.1:8000/tasks/1" ^
  -H "Content-Type: application/json" ^
  -d "{\"done\":true}"
```

### Delete a task

```bash
curl -X DELETE "http://127.0.0.1:8000/tasks/1"
```

### Search tasks

```bash
curl "http://127.0.0.1:8000/tasks?search=milk"
```

### Filter completed tasks

```bash
curl "http://127.0.0.1:8000/tasks?done=true"
```

### Get statistics

```bash
curl http://127.0.0.1:8000/stats
```

## How to Run

### Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn

### Activate the Virtual Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Install Dependencies

```bash
pip install "fastapi[standard]"
```

### Start the Server

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## SQLite Database Operations

The database can be inspected using **DB Browser for SQLite**.

### View all tasks

```sql
SELECT * FROM tasks;
```

### View completed tasks

```sql
SELECT * FROM tasks
WHERE done = 1;
```

### Count all tasks

```sql
SELECT COUNT(*) FROM tasks;
```

### View tasks alphabetically

```sql
SELECT * FROM tasks
ORDER BY title;
```

### Update a task

```sql
UPDATE tasks
SET done = 1
WHERE id = 1;
```

### Delete a task

```sql
DELETE FROM tasks
WHERE id = 1;
```

## Screenshots

### Swagger UI

![Swagger UI](screenshots/swagger-ui.png)

### GET /tasks Response

![GET /tasks Response](screenshots/task-api-example.png)

### POST /tasks Request

![POST /tasks Request](screenshots/post-task-request.png)

### SQLite Database

![SQLite Database](screenshots/sqlite-database.png)

The SQLite screenshot shows the `tasks` table in DB Browser for SQLite with the stored task data.

## Notes

- The application uses SQLite for persistent task storage.
- The database file is `tasks.db`.
- The `tasks` table is created automatically when the application starts.
- Three sample tasks are inserted only when the table is empty.
- Task IDs are automatically generated by SQLite using `AUTOINCREMENT`.
- Tasks persist after restarting the FastAPI server.
- Search and status filtering are performed directly using SQL.
- Alphabetical sorting is performed using SQL's `ORDER BY title`.
- Task statistics are calculated using SQL's `COUNT(*)`.
- User-provided values are passed to SQL using parameterized queries.
- `created_at` is set when a task is created.
- `updated_at` is changed whenever a task is updated.
- The database can be inspected using DB Browser for SQLite.
- `tasks.db` is kept local and is not committed to the repository.

## Future Improvements

Possible future improvements include:

- Database migrations
- Pagination
- Authentication
- More advanced task filtering
- Additional task fields

## Star This Project

If you found this project useful, please show your support by starring the repository on GitHub.

⭐ Star this repo if you like it!