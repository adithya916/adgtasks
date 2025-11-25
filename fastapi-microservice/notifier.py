from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Notification Service", description="Simple notification logger")

class NotificationPayload(BaseModel):
    submission_id: int
    task_id: int
    submitter_name: str

@app.post("/notify")
def notify(payload: NotificationPayload):
    """
    Receives notification of a new submission and logs it.
    """
    print(f"Received notification: Submission ID {payload.submission_id} for Task ID {payload.task_id} by {payload.submitter_name}")
    return {"status": "received"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

