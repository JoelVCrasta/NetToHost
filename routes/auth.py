from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from clients.supabase_client import get_current_user, supabase

router = APIRouter()


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignInResponse(BaseModel):
    status: str
    access_token: str
    user_id: str
    email: EmailStr
    display_name: str
    avatar_url: Optional[str] = None


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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/signin", response_model=SignInResponse)
def signin_email(payload: SignInRequest, res: Response):
    try:
        auth_res = supabase.auth.sign_in_with_password(
            {
                "email": payload.email,
                "password": payload.password,
            }
        )

        if not auth_res.session or not auth_res.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
            )

        res.set_cookie(
            key="refresh_token",
            value=auth_res.session.refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 3600,  # 7 days
        )

        user_metadata = auth_res.user.user_metadata or {}

        return SignInResponse(
            status="success",
            access_token=auth_res.session.access_token,
            user_id=auth_res.user.id,
            email=auth_res.user.email,
            display_name=user_metadata.get("display_name", "Unknown"),
            avatar_url=user_metadata.get("avatar_url"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/signout")
def logout(res: Response, user=Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
        res.delete_cookie("refresh_token")
        return {"status": "success", "message": "Signed out successfully."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))