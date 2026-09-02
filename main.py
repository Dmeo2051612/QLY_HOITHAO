import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal




cred = credentials.Certificate("key.json")
if not firebase_admin._apps: 
    firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI(title="Hệ thống Quản lý Hội thảo")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_now():
    return datetime.now(timezone.utc).isoformat()








class UserModel(BaseModel):
    name: str
    email: str
    role: Literal["author", "reviewer", "organizer", "attendee"]

class ConferenceModel(BaseModel):
    title: str
    description: str
    start_date: str
    end_date: str

class SubmissionModel(BaseModel):
    conference_id: str
    author_id: str
    title: str
    abstract: str
    keywords: List[str]
    track: str
    file_url: str
    status: str = "pending"  
class ScoreModel(BaseModel):
    originality: int
    presentation: int
    technical_quality: int

class ReviewModel(BaseModel):
    submission_id: str
    reviewer_id: str
    scores: ScoreModel
    comments: str

class RegistrationModel(BaseModel):
    conference_id: str
    user_id: str

class ReviewAssignmentModel(BaseModel):
    submission_id: str
    reviewer_id: str





@app.get("/api/users")
async def get_users():
    docs = db.collection("users").stream()
    return {"success": True, "data": [{"id": d.id, **d.to_dict()} for d in docs]}



@app.post("/api/users")
async def create_user(data: UserModel):
    payload = data.model_dump()
    payload["created_at"] = get_now()
    payload["updated_at"] = payload["created_at"]
    doc_ref = db.collection("users").document()
    doc_ref.set(payload)
    return {"success": True, "id": doc_ref.id}



@app.put("/api/users/{user_id}")
async def update_user(user_id: str, data: UserModel):
    doc_ref = db.collection("users").document(user_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    payload = data.model_dump()
    payload["updated_at"] = get_now()
    doc_ref.set(payload, merge=True)
    return {"success": True, "message": "Đã cập nhật người dùng"}




@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str):
    doc_ref = db.collection("users").document(user_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    doc_ref.delete()
    return {"success": True, "message": "Đã xóa người dùng"}







@app.get("/api/conferences")
async def get_conferences():
    docs = db.collection("conferences").stream()
    return {"success": True, "data": [{"id": d.id, **d.to_dict()} for d in docs]}


@app.post("/api/conferences")
async def create_conference(data: ConferenceModel):
    payload = data.model_dump()
    payload["created_at"] = get_now()
    payload["updated_at"] = payload["created_at"]
    doc_ref = db.collection("conferences").document()
    doc_ref.set(payload)
    return {"success": True, "id": doc_ref.id}


@app.put("/api/conferences/{conference_id}")
async def update_conference(conference_id: str, data: ConferenceModel):
    doc_ref = db.collection("conferences").document(conference_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Không tìm thấy hội thảo")
    payload = data.model_dump()
    payload["updated_at"] = get_now()
    doc_ref.set(payload, merge=True)
    return {"success": True, "message": "Đã cập nhật hội thảo"}




@app.delete("/api/conferences/{conference_id}")
async def delete_conference(conference_id: str):
    doc_ref = db.collection("conferences").document(conference_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Không tìm thấy hội thảo")
    doc_ref.delete()
    return {"success": True, "message": "Đã xóa hội thảo"}







@app.get("/api/submissions/{conference_id}")
async def get_submissions_by_conference(conference_id: str):
    query = db.collection("submissions").where("conference_id", "==", conference_id).stream()
    return {"success": True, "data": [{"id": d.id, **d.to_dict()} for d in query]}

@app.post("/api/submissions")
async def create_submission(data: SubmissionModel):
    payload = data.model_dump()
    payload["created_at"] = get_now()
    payload["updated_at"] = payload["created_at"]
    doc_ref = db.collection("submissions").document()
    doc_ref.set(payload)
    return {"success": True, "id": doc_ref.id}

@app.put("/api/submissions/{submission_id}")
async def update_submission(submission_id: str, data: SubmissionModel):
    doc_ref = db.collection("submissions").document(submission_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài nộp")
    payload = data.model_dump()
    payload["updated_at"] = get_now()
    doc_ref.set(payload, merge=True)
    return {"success": True, "message": "Đã cập nhật bài nộp"}

@app.delete("/api/submissions/{submission_id}")
async def delete_submission(submission_id: str):
    doc_ref = db.collection("submissions").document(submission_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài nộp")
    doc_ref.delete()
    return {"success": True, "message": "Đã xóa bài nộp"}







@app.get("/api/reviews/{submission_id}")
async def get_reviews(submission_id: str):
    query = db.collection("reviews").where("submission_id", "==", submission_id).stream()
    return {"success": True, "data": [{"id": d.id, **d.to_dict()} for d in query]}

@app.post("/api/reviews")
async def create_review(data: ReviewModel):
    payload = data.model_dump()
    payload["created_at"] = get_now()
    payload["updated_at"] = payload["created_at"]
    doc_ref = db.collection("reviews").document()
    doc_ref.set(payload)
    return {"success": True, "id": doc_ref.id}

@app.put("/api/reviews/{review_id}")
async def update_review(review_id: str, data: ReviewModel):
    doc_ref = db.collection("reviews").document(review_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Không tìm thấy đánh giá")
    payload = data.model_dump()
    payload["updated_at"] = get_now()
    doc_ref.set(payload, merge=True)
    return {"success": True, "message": "Đã cập nhật đánh giá"}

@app.delete("/api/reviews/{review_id}")
async def delete_review(review_id: str):
    doc_ref = db.collection("reviews").document(review_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Không tìm thấy đánh giá")
    doc_ref.delete()
    return {"success": True, "message": "Đã xóa đánh giá"}







@app.get("/api/registrations/{conference_id}")
async def get_registrations(conference_id: str):
    query = db.collection("registrations").where("conference_id", "==", conference_id).stream()
    return {"success": True, "data": [{"id": d.id, **d.to_dict()} for d in query]}

@app.post("/api/registrations")
async def create_registration(data: RegistrationModel):
    payload = data.model_dump()
    payload["created_at"] = get_now()
    doc_ref = db.collection("registrations").document()
    doc_ref.set(payload)
    return {"success": True, "id": doc_ref.id}

@app.delete("/api/registrations/{registration_id}")
async def delete_registration(registration_id: str):
    doc_ref = db.collection("registrations").document(registration_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Không tìm thấy lượt đăng ký")
    doc_ref.delete()
    return {"success": True, "message": "Đã hủy đăng ký tham dự"}






@app.get("/api/review-assignments/{submission_id}")
async def get_review_assignments(submission_id: str):
    query = db.collection("review_assignments").where("submission_id", "==", submission_id).stream()
    return {"success": True, "data": [{"id": d.id, **d.to_dict()} for d in query]}

@app.post("/api/review-assignments")
async def create_review_assignment(data: ReviewAssignmentModel):
    payload = data.model_dump()
    payload["created_at"] = get_now()
    doc_ref = db.collection("review_assignments").document()
    doc_ref.set(payload)
    return {"success": True, "id": doc_ref.id}

@app.delete("/api/review-assignments/{assignment_id}")
async def delete_review_assignment(assignment_id: str):
    doc_ref = db.collection("review_assignments").document(assignment_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Không tìm thấy phân công")
    doc_ref.delete()
    return {"success": True, "message": "Đã xóa phân công phản biện"}