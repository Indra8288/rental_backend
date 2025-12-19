from sqlalchemy.orm import Session
from app.models.customer import Customer

def create_customer(db: Session, cust: Customer) -> Customer:
    db.add(cust)
    db.commit()
    db.refresh(cust)
    return cust
