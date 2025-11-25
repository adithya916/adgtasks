import sqlite3
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List
import httpx

app = FastAPI(title="Task Microservice", description="Core business logic for tasks and submissions")

DB_NAME = "tasks.db"
MAX_SUBMISSIONS = 3
NOTIFICATION_SERVICE_URL = "http://localhost:8001/notify"

class TaskCreate(BaseModel):
    title: str
    description: str

class Task(BaseModel):
    id: int
    title: str
    description: str
    status: str

class SubmissionCreate(BaseModel):
    submitter_name: str
    content: str

class Submission(BaseModel):
    id: int
    task_id: int
    submitter_name: str
    content: str

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Open'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            submitter_name TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

init_db()

@app.get("/tasks", response_model=List[Task])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return dict(row)

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)",
            (task.title, task.description, 'Open')
        )
        conn.commit()
        new_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (new_id,))
        row = cursor.fetchone()
        return dict(row)
    finally:
        conn.close()

@app.post("/tasks/{task_id}/submit", response_model=Submission, status_code=status.HTTP_201_CREATED)
async def create_submission(task_id: int, submission: SubmissionCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    submission_data = None
    
    try:
        with conn:
            cursor.execute("BEGIN IMMEDIATE")
            
            cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Task not found")
            
            cursor.execute("SELECT COUNT(*) as count FROM submissions WHERE task_id = ?", (task_id,))
            count_result = cursor.fetchone()
            submission_count = count_result['count'] if count_result else 0
            
            if submission_count >= MAX_SUBMISSIONS:
                raise HTTPException(status_code=409, detail="Max submissions reached")
            
            cursor.execute(
                "INSERT INTO submissions (task_id, submitter_name, content) VALUES (?, ?, ?)",
                (task_id, submission.submitter_name, submission.content)
            )
            new_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM submissions WHERE id = ?", (new_id,))
            row = cursor.fetchone()
            submission_data = dict(row)
            
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()
        
    if submission_data:
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "submission_id": submission_data["id"],
                    "task_id": submission_data["task_id"],
                    "submitter_name": submission_data["submitter_name"]
                }
                await client.post(NOTIFICATION_SERVICE_URL, json=payload)
        except Exception as e:
            print(f"Failed to send notification: {e}")

    return submission_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
