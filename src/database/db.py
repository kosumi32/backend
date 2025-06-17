from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models

def get_challenge_quota(db: Session, user_id: str):
    """
    Get the challenge quota for a specific user.
    If the user does not exist, create a new entry with default quota.
    """
    quota = (db.query(models.ChallengeQuota)    # specify what table/ model to query
    .filter(models.ChallengeQuota.user_id == user_id)   # criteria
    .first())
    
    if not quota:
        # Create a new quota entry with default values
        quota = models.ChallengeQuota(user_id=user_id, quota=15, last_reset_date= datetime.now())
        db.add(quota)
        db.commit()
        db.refresh(quota)  # Refresh to get the updated object with ID
    return quota


def create_challenge_quota(db: Session, user_id: str):
    """
    Create a new challenge quota for a user.
    This is used when the user is created.
    """
    quota = models.ChallengeQuota(user_id= user_id)
    db.add(quota)
    db.commit()
    db.refresh(quota)  # Refresh to get the updated object with ID
    return quota


def reset_quota_if_needed(db: Session, quota: models.ChallengeQuota):

    # Check if the last reset date is more than 24 hours ago
    if datetime.now() - quota.last_reset_date > timedelta(hours=24):
        quota.quota = 15  # Reset to default quota
        quota.last_reset_date = datetime.now()  # Update the last reset date
        db.commit()
        db.refresh(quota)  # Refresh to get the updated object
    return quota
 

def create_challenge(db: Session, difficulty: str, created_by: str, title: str, options: str, correct_answer_id: int, explanation: str):
    """
    Create a new challenge in the database.
    """
    challenge = models.Challenge(
        difficulty= difficulty,
        created_by= created_by,
        title= title,
        options= options,
        correct_answer_id= correct_answer_id,
        explanation= explanation  # Fixed spelling from explaination to explanation
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)  # Refresh to get the updated object with ID
    return challenge


def get_user_challenges(db: Session, user_id: str):
    """
    Get all challenges created by a specific user.
    """
    challenges = db.query(models.Challenge).filter(models.Challenge.created_by == user_id).all()

    return challenges