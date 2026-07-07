from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from auth.supabase_client import supabase, get_current_user

router = APIRouter()


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup")
def signup_email(payload: SignUpRequest):
    try:
        response = supabase.auth.sign_up(
            {
                "email": payload.email,
                "password": payload.password,
                "options": {
                    "data": {
                        "display_name": payload.display_name,
                        "avatar_url": None,
                        "role": "user",
                    }
                },
            }
        )

        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register account.",
            )

        return {"status": "success", "message": "Signed up successfully."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/signin")
def signin_email(payload: SignInRequest):
    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": payload.email,
                "password": payload.password,
            }
        )

        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
            )

        user_metadata = response.user.user_metadata or {}
        display_name = user_metadata.get("display_name", "Unknown")

        return {
            "status": "success",
            "access_token": response.session.access_token,
            "user_id": response.user.id,
            "display_name": display_name,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/signout")
def logout(user=Depends(get_current_user)):
    try:
        return {"status": "success", "message": "Signed out successfully."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
