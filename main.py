from datetime import datetime
from pydantic import BaseModel
from fastapi import FastAPI, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import Base, Sale
from database import SessionLocal, engine
from forecasting import forecast_with_dynamic_features

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    forecast_list = forecast_with_dynamic_features(db)

    past_sales = db.query(Sale).order_by(desc(Sale.sale_date)).limit(20).all()

    past_sales_list = [
        {
            'item_id': sale.item_id,
            'date': sale.sale_date.strftime('%Y-%m-%d'),
            'quantity': sale.quantity
        }
        for sale in past_sales
    ]

    return templates.TemplateResponse(request, "index.html", {
        "forecast": forecast_list,
        "past_sales": past_sales_list
    })

@app.post("/add_sale")
def add_sale(
    sale_date: str = Form(...),
    quantity: int = Form(...),
    item_id: int = Form(...),
    db: Session = Depends(get_db)
):
    sale_date = datetime.strptime(sale_date, '%Y-%m-%d').date()
    new_sale = Sale(sale_date=sale_date, quantity=quantity, item_id=item_id)
    db.add(new_sale)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


class SaleCreate(BaseModel):
    sale_date: datetime
    quantity: int
    item_id: int

@app.post("/sales")
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    db_sale = Sale(sale_date=sale.sale_date.date(), quantity=sale.quantity, item_id=sale.item_id)
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return {
        "message": "Продажа успешно добавлена.",
        "sale": {
            "sale_date": db_sale.sale_date,
            "quantity": db_sale.quantity,
            "item_id": db_sale.item_id
        }
    }