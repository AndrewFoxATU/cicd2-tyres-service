# backend/tyres_service/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from decimal import Decimal

from app.database import engine, SessionLocal
from app.models import Base, TyreModel
from app.schemas import TyreCreate, TyreSchema, TyreUpdate
from app.auth import TokenUser, get_current_user, require_roles




@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
app = FastAPI(lifespan=lifespan)


ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def commit_or_rollback(db: Session, msg: str):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=msg)



@app.get("/health")
def health():
    return {"status": "ok"}


# ===============================================
#                  TYRES CRUD
# ===============================================

# -----------------------------
# CREATE TYRE (admin / employee+)
# -----------------------------
@app.post("/api/tyres", status_code=201)
def create_tyre(
    payload: TyreCreate,
    db: Session = Depends(get_db),
    _user: TokenUser = Depends(require_roles("admin", "employee+")),
):
    data = payload.model_dump()

    data["retail_cost"] = (data["cost"] * Decimal("1.35")).quantize(Decimal("0.01"))

    tyre = TyreModel(**data)
    db.add(tyre)
    commit_or_rollback(db, "Tyre could not be created")
    db.refresh(tyre)
    return tyre


# -----------------------------
# LIST TYRES
# -----------------------------
@app.get("/api/tyres")
def list_tyres(
    db: Session = Depends(get_db),
    _user: TokenUser = Depends(get_current_user),
):
    stmt = select(TyreModel).order_by(TyreModel.id)
    return db.execute(stmt).scalars().all()


# -----------------------------
# GET TYRE BY ID
# -----------------------------
@app.get("/api/tyres/{tyre_id}")
def get_tyre(
    tyre_id: int,
    db: Session = Depends(get_db),
    _user: TokenUser = Depends(get_current_user),
):
    tyre = db.get(TyreModel, tyre_id)
    if not tyre:
        raise HTTPException(status_code=404, detail="Tyre not found")
    return tyre


# -----------------------------
# UPDATE TYRE (PUT, admin / employee+)
# -----------------------------
@app.put("/api/tyres/{tyre_id}")
def update_tyre_put(
    tyre_id: int,
    payload: TyreSchema,
    db: Session = Depends(get_db),
    _user: TokenUser = Depends(require_roles("admin", "employee+")),
):
    tyre = db.get(TyreModel, tyre_id)
    if not tyre:
        raise HTTPException(status_code=404, detail="Tyre not found")

    data = payload.model_dump()
    data.pop("retail_cost", None)

    data["retail_cost"] = (data["cost"] * Decimal("1.35")).quantize(Decimal("0.01"))

    for field, value in data.items():
        setattr(tyre, field, value)

    commit_or_rollback(db, "Failed to update tyre")
    db.refresh(tyre)
    return tyre


# -----------------------------
# PARTIAL UPDATE (PATCH, admin / employee+ / service)
# "service" is the orders service adjusting stock during a sale.
# -----------------------------
@app.patch("/api/tyres/{tyre_id}")
def update_tyre_patch(
    tyre_id: int,
    payload: TyreUpdate,
    db: Session = Depends(get_db),
    _user: TokenUser = Depends(require_roles("admin", "employee+", "service")),
):
    tyre = db.get(TyreModel, tyre_id)
    if not tyre:
        raise HTTPException(status_code=404, detail="Tyre not found")

    update_data = payload.model_dump(exclude_unset=True)
    update_data.pop("retail_cost", None)  # cannot be changed manually

    if "cost" in update_data:
        update_data["retail_cost"] = (
            update_data["cost"] * Decimal("1.35")
        ).quantize(Decimal("0.01"))

    for field, value in update_data.items():
        setattr(tyre, field, value)

    commit_or_rollback(db, "Failed to update tyre")
    db.refresh(tyre)
    return tyre


# -----------------------------
# DELETE TYRE (admin / employee+)
# -----------------------------
@app.delete("/api/tyres/{tyre_id}", status_code=204)
def delete_tyre(
    tyre_id: int,
    db: Session = Depends(get_db),
    _user: TokenUser = Depends(require_roles("admin", "employee+")),
) -> Response:
    tyre = db.get(TyreModel, tyre_id)
    if not tyre:
        raise HTTPException(status_code=404, detail="Tyre not found")
    
    db.delete(tyre)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
