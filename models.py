from sqlalchemy import Column, Integer, Date, UniqueConstraint
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True, index=True)
    sale_date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False)
    item_id = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('sale_date', 'item_id', name='unique_sale_date_item'),
    )
