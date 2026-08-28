# Task API

A simple FastAPI-based task management API with CRUD endpoints for tasks and SQLite database storage.

---

## Introduction

FastAPI is a Python framework used to build APIs quickly and easily. It is beginner-friendly and helps you create web services with less code. It also provides automatic validation and built-in documentation, which makes testing the API easier.

This project is a small task management API. You can use it to create tasks, view all tasks, view one task by ID, update a task, or delete a task.

The application uses SQLite to persist task data so that tasks remain available even after the FastAPI server is restarted.

An API endpoint is simply a web address that performs a specific action. For example, `/tasks` is used to view or create tasks, and `/tasks/{task_id}` is used to work with one specific task.

FastAPI also provides a Swagger page at `/docs`, where you can see all endpoints and try them directly in your browser.

---

## Features

- Create new tasks
- Retrieve all tasks
- Retrieve a single task by ID
- Update an existing task
- Delete a task
- Filter tasks by completion status
- Search tasks by title
- Built-in health check endpoint
- Interactive API documentation at `/docs`
- Persistent SQLite database storage
- Direct database inspection using DB Browser for SQLite

---

## Project Structure

```text
main.py
routes.py
schemas.py
database.py
tasks.db
README.md
screenshots/