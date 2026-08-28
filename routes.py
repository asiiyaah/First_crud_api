from fastapi import APIRouter, HTTPException, status
from schemas import TaskCreate, TaskUpdate, TaskResponse
from database import get_connection

router = APIRouter()


# --------------------------------------------------
# RESET
# --------------------------------------------------

@router.post("/reset")
def reset_tasks():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM tasks")

    sample_tasks = [
        ("Buy groceries", 0),
        ("Do homework", 1),
        ("Do the dishes", 0)
    ]

    cursor.executemany(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        sample_tasks
    )

    connection.commit()
    connection.close()

    return {
        "message": "Tasks reset successfully"
    }


# --------------------------------------------------
# STATS
# --------------------------------------------------

@router.get("/stats")
def get_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = ?", (1,))
    done = cursor.fetchone()[0]

    connection.close()

    return {
        "total": total,
        "done": done,
        "open": total - done
    }


# --------------------------------------------------
# GET ALL TASKS
# --------------------------------------------------

@router.get("/tasks")
def get_tasks(
    done: bool | None = None,
    search: str | None = None
):
    connection = get_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM tasks"
    parameters = []

    conditions = []

    # Filter by completion status
    if done is not None:
        conditions.append("done = ?")
        parameters.append(1 if done else 0)

    # Filter by title
    if search is not None:
        conditions.append("title LIKE ?")
        parameters.append(f"%{search}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, parameters)

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"])
        }
        for row in rows
    ]


# --------------------------------------------------
# GET ONE TASK
# --------------------------------------------------

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task_byid(task_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }


# --------------------------------------------------
# CREATE TASK
# --------------------------------------------------

@router.post(
    "/tasks",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponse
)
def post_task(task_input: TaskCreate):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task_input.title, 0)
    )

    task_id = cursor.lastrowid

    connection.commit()

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    row = cursor.fetchone()

    connection.close()

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }

# --------------------------------------------------
# UPDATE TASK
# --------------------------------------------------

@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task_id: int,
    task_update_input: TaskUpdate
):
    if (
        task_update_input.title is None
        and task_update_input.done is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty body not allowed"
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    row = cursor.fetchone()

    if row is None:
        connection.close()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    new_title = (
        task_update_input.title
        if task_update_input.title is not None
        else row["title"]
    )

    new_done = (
        1 if task_update_input.done
        else 0
        if task_update_input.done is not None
        else row["done"]
    )

    cursor.execute(
        """
        UPDATE tasks
        SET title = ?, done = ?
        WHERE id = ?
        """,
        (new_title, new_done, task_id)
    )

    connection.commit()

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    updated_row = cursor.fetchone()

    connection.close()

    return {
        "id": updated_row["id"],
        "title": updated_row["title"],
        "done": bool(updated_row["done"])
    }


# --------------------------------------------------
# DELETE TASK
# --------------------------------------------------

@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)

def delete_task(task_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    row = cursor.fetchone()

    if row is None:
        connection.close()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    connection.commit()
    connection.close()

    return