from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from datetime import datetime


class ProductOut(BaseModel):
    id: str
    code: str
    name: str
    type: str
    price: Decimal
    stock: int
    art_class: Optional[str] = None
    emoji: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int
    unit_price: Decimal


class OrderItemOut(BaseModel):
    id: int
    product_id: str
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    shipping_address: Optional[str] = None
    payment_method: str
    total_amount: Decimal


class OrderOut(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    customer_phone: Optional[str]
    shipping_address: Optional[str]
    payment_method: str
    total_amount: Decimal
    status: str
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        from_attributes = True
