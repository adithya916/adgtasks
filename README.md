# Task Management System

A microservices-based application demonstrating a hybrid Node.js/Python architecture.

## Services

1.  **Gateway Service (Node.js/Express)** - Port 3000
    *   Public facing API
    *   Proxies requests to the internal microservice

2.  **Task Microservice (Python/FastAPI)** - Port 8000
    *   Core business logic
    *   SQLite persistence
    *   Enforces submission limits

3.  **Notification Service (Python/FastAPI)** - Port 8001
    *   Receives asynchronous notifications about new submissions

## Setup & Running

### Prerequisites
*   Node.js (v14+)
*   Python (v3.8+)

### 1. Start Notification Service
```bash
cd fastapi-microservice
pip install -r requirements.txt
python notifier.py
```

### 2. Start Task Microservice
In a new terminal:
```bash
cd fastapi-microservice
python main.py
```

### 3. Start Gateway
In a new terminal:
```bash
cd express-gateway
npm install
node server.js
```

## API Usage

### Create Task
```bash
POST http://localhost:3000/tasks
{
    "title": "My Task",
    "description": "Task description"
}
```

### Submit Solution
```bash
POST http://localhost:3000/tasks/{id}/submit
{
    "submitter_name": "User",
    "content": "My solution"
}
```
*Note: Maximum 3 submissions per task.*

