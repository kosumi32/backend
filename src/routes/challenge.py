from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..ai_generator import generate_challenge_with_ai

from ..database.db import (
    get_challenge_quota,
    create_challenge_quota,
    reset_quota_if_needed,
    create_challenge,
    get_user_challenges
)

from ..utils import authenticate_and_get_user_details
from ..database.models import get_db

import json 
from datetime import datetime

# Making code more modular
router = APIRouter()

# Schema (FastAPI)- validate data being sent to endpoint is correct
# What we expecting in the request, thus API check it
class ChallengeRequest(BaseModel):
    difficulty: str
    
    class Config:   # Display example if an error
        json_schema_extra = {"example": {"difficulty": "easy"}}  # Example for API documentation


# API endpoint
@router.post("/generate-challenge")
async def generate_challenge(request: ChallengeRequest, request_obj: Request, db: Session = Depends(get_db)):     # FastAPI expects a JSON body with the ChallengeRequest schema (Json body validator)

    # we have 2 seperate things
    # 1. Details expecting from the user (ChallengeRequest)
    # 2. reuest_obj: Actual reqquest including headers, cookies, etc. (Raw HTTP request)
    try:
        user_details = authenticate_and_get_user_details(request_obj)
        user_id= user_details.get("user_id")

        quota= get_challenge_quota(db, user_id)
        if not quota:
            quota= create_challenge_quota(db, user_id)  # create a new quota if it does not exist

        quota = reset_quota_if_needed(db, quota)  # reset quota if needed

        if quota.quota <= 0:
            raise HTTPException(status_code=403, detail="Quota exceeded. Please try again later.")
        
        challenge_date= generate_challenge_with_ai(request.difficulty)
        
        new_challenge= create_challenge(
            db=db,
            difficulty= request.difficulty,
            created_by=user_id,
            title=challenge_date["title"],
            options=json.dumps(challenge_date["options"]),  # Convert Python list to JSON string
            correct_answer_id=challenge_date["correct_answer_id"],
            explaination=challenge_date["explanation"],  # Fixed: parameter name should be 'explaination' to match db function
        )

        # db.flush()  # Assigns new_challenge.id immediately        
        quota.quota -= 1  # Decrease the quota by 1
        # db.add(quota)  # Add the updated quota to the session
        db.commit()

        return {
            "id": new_challenge.id,
            "difficulty": request.difficulty,
            "title": new_challenge.title,
            "options": json.loads(new_challenge.options),  # Convert JSON string to Python list
            "correct_answer_id": new_challenge.correct_answer_id,
            "explanation": new_challenge.explaination,  # Fixed: accessing the correct field name from model
            "timestamp": new_challenge.date_created,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/my-history")
async def my_history(request: Request, db: Session = Depends(get_db)):      # auto get db session/ Raw HTTP request (X Json)
    user_details = authenticate_and_get_user_details(request)     # authenticate user and get details
    # if not user_details:
    #     raise HTTPException(status_code=401, detail="Unauthorized User")

    user_id = user_details.get("user_id")

    challenges = get_user_challenges(db, user_id)
    return {"challenges": challenges}


@router.get("/quota")
async def get_quota(request: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)     # authenticate user and get details
    # if not user_details:
    #     raise HTTPException(status_code=401, detail="Unauthorized User")
    
    user_id = user_details.get("user_id")

    quota = get_challenge_quota(db, user_id)
    if not quota:   # if quota does not exist, create a new one
        return {
            "user_id": user_id,
            "quota": 0,
            "last_reset_date": datetime.now(),
        }
    quota = reset_quota_if_needed(db, quota)  # reset quota if needed
    return quota