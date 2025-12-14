# backend/tyres_service/app/load_csv.py
import csv
from decimal import Decimal
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, TyreModel

Base.metadata.create_all(bind=engine)


CSV_FILE = "tyredatabase.csv"

def to_bool(value: str) -> bool:
    return str(value).strip().lower() in ("true", "1", "yes")

def load_csv():
    db: Session = SessionLocal()
    try:
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                cost = Decimal(str(row["cost"]))
                retail_cost = (cost * Decimal("1.35")).quantize(Decimal("0.01"))
                tyre = TyreModel(
                    brand=row["Brand"].strip(),
                    model=row["Model"].strip(),
                    size=row["size"].strip(),
                    load_rate=int(row["load_rate"]),
                    speed_rate=row["speed_rate"].strip().upper(),
                    season=row["Season"].strip().title(),
                    supplier=row["Supplier"].strip(),
                    fuel_efficiency=row["Fuel_Efficiency"].strip().upper(),
                    noise_level=int(row["noise_level"]),
                    weather_efficiency=row["weather_efficiency"].strip().upper(),
                    ev_approved=to_bool(row["ev_approved"]),
                    cost=cost,
                    quantity=int(row["quantity"]),
                    retail_cost=retail_cost,
                )
                db.add(tyre)
                count += 1

            db.commit()
            print(f"Successfully inserted {count} tyres into the database.")

    except FileNotFoundError:
        print(f"Could not find CSV file: {CSV_FILE}")
    finally:
        db.close()

if __name__ == "__main__":
    load_csv()
