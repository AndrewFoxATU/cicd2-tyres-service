# backend/tyres_service/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from decimal import Decimal

from database import engine, SessionLocal
from models import Base, TyreModel
from schemas import TyreCreate, TyreSchema, TyreUpdate



@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
# CREATE TYRE
# -----------------------------
@app.post("/api/tyres", status_code=201)
def create_tyre(payload: TyreCreate, db: Session = Depends(get_db)):
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
def list_tyres(db: Session = Depends(get_db)):
    stmt = select(TyreModel).order_by(TyreModel.id)
    return db.execute(stmt).scalars().all()


# -----------------------------
# GET TYRE BY ID
# -----------------------------
@app.get("/api/tyres/{tyre_id}")
def get_tyre(tyre_id: int, db: Session = Depends(get_db)):
    tyre = db.get(TyreModel, tyre_id)
    if not tyre:
        raise HTTPException(status_code=404, detail="Tyre not found")
    return tyre


# -----------------------------
# UPDATE TYRE (PUT)
# -----------------------------
@app.put("/api/tyres/{tyre_id}")
def update_tyre_put(tyre_id: int, payload: TyreSchema, db: Session = Depends(get_db)):
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
# PARTIAL UPDATE (PATCH)
# -----------------------------
@app.patch("/api/tyres/{tyre_id}")
def update_tyre_patch(tyre_id: int, payload: TyreUpdate, db: Session = Depends(get_db)):
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
# DELETE TYRE
# -----------------------------
@app.delete("/api/tyres/{tyre_id}", status_code=204)
def delete_tyre(tyre_id: int, db: Session = Depends(get_db)) -> Response:
    tyre = db.get(TyreModel, tyre_id)
    if not tyre:
        raise HTTPException(status_code=404, detail="Tyre not found")
    
    db.delete(tyre)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
