from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .ai_service import get_fitness_ai
from .database import User, WorkoutPlan, get_db, get_user_with_plan
from .schemas import FeedbackRequest, FeedbackResponse, PlanResponse, UserInput

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


def _plan_response(user: User) -> PlanResponse:
    if not user.plan:
        raise HTTPException(status_code=404, detail="No plan found for this user")
    return PlanResponse(
        user_id=user.id,
        name=user.name,
        age=user.age,
        weight=user.weight,
        goal=user.goal,
        intensity=user.intensity,
        workout_plan=user.plan.original_plan,
        nutrition_tip=user.plan.nutrition_tip,
        updated_plan=user.plan.updated_plan,
    )


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout_form(
    request: Request,
    user_id: int = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        payload = UserInput(user_id=user_id, name=name, age=age, weight=weight, goal=goal, intensity=intensity)
        result = generate_plan(payload, db)
        return templates.TemplateResponse(request=request, name="result.html", context={"plan": result.model_dump(), "message": None})
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="index.html", context={"error": str(exc)}, status_code=400)


@router.post("/api/generate-plan", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def generate_plan(payload: UserInput, db: Session = Depends(get_db)) -> PlanResponse:
    ai = get_fitness_ai()
    user = get_user_with_plan(db, payload.user_id)
    if not user:
        user = User(id=payload.user_id, name=payload.name, age=payload.age, weight=payload.weight, goal=payload.goal, intensity=payload.intensity)
        db.add(user)
    else:
        user.name, user.age, user.weight, user.goal, user.intensity = payload.name, payload.age, payload.weight, payload.goal, payload.intensity
    plan_text = ai.generate_workout(age=payload.age, weight=payload.weight, goal=payload.goal, intensity=payload.intensity)
    tip = ai.generate_nutrition_tip(payload.goal)
    if user.plan:
        user.plan.original_plan, user.plan.updated_plan, user.plan.feedback, user.plan.nutrition_tip = plan_text, None, None, tip
    else:
        user.plan = WorkoutPlan(original_plan=plan_text, nutrition_tip=tip)
    db.commit()
    db.refresh(user)
    return _plan_response(user)


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback_form(request: Request, user_id: int = Form(...), feedback: str = Form(...), db: Session = Depends(get_db)):
    try:
        result = update_plan(user_id, FeedbackRequest(user_id=user_id, feedback=feedback), db)
        user = get_user_with_plan(db, user_id)
        return templates.TemplateResponse(request=request, name="result.html", context={"plan": _plan_response(user).model_dump(), "message": result.message})
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="index.html", context={"error": str(exc)}, status_code=400)


@router.post("/api/update-plan/{user_id}", response_model=FeedbackResponse)
def update_plan(user_id: int, payload: FeedbackRequest, db: Session = Depends(get_db)) -> FeedbackResponse:
    if user_id != payload.user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    user = get_user_with_plan(db, user_id)
    if not user or not user.plan:
        raise HTTPException(status_code=404, detail="Original plan not found for this user")
    updated = get_fitness_ai().update_workout(user.plan.original_plan, payload.feedback)
    user.plan.updated_plan, user.plan.feedback = updated, payload.feedback
    db.commit()
    return FeedbackResponse(message="Your plan has been updated based on your feedback.", updated_plan=updated)


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.id)).all()
    return templates.TemplateResponse(request=request, name="all_users.html", context={"users": users})


@router.get("/api/users", response_model=list[PlanResponse])
def list_users(db: Session = Depends(get_db)):
    return [_plan_response(user) for user in db.scalars(select(User).order_by(User.id)).all() if user.plan]


@router.get("/api/users/{user_id}", response_model=PlanResponse)
def get_user_plan(user_id: int, db: Session = Depends(get_db)):
    user = get_user_with_plan(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _plan_response(user)
