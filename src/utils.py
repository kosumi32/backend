from clerk_backend_api import Clerk, AuthenticateRequestOptions
import os
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

clerk_sdk= Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

# request (frontend) to backend
# Verify is it valid request
def authenticate_and_get_user_details(request):
    try:
        request_state= clerk_sdk.authenticate_request(
            request,
            AuthenticateRequestOptions(
                authorized_parties=["http://localhost:5173", "http://localhost:5174"], 
                jwt_key= os.getenv("JWT_KEY")      # serverless (bypass sending to clerk server)
                # Either way works, with or without
            )
            )
        if not request_state.is_signed_in:
            # If the user is not signed in, raise an HTTP exception
            raise HTTPException(status_code=401, detail="Invalid authenticated")

        # return the user details (UserID)
        user_id = request_state.payload.get("sub")

        return {"user_id": user_id}

    except Exception as e:
        # If authentication fails, raise an HTTP exception
        raise HTTPException(status_code=500, detail= str(e))