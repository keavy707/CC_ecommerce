from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from app.database import get_db
from app.models import Order, OrderItem, Product
from app.schemas import OrderCreate, OrderOut
from typing import List

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/", response_model=OrderOut)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    # Validate stock
    for item in payload.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}"
            )

    # Create order
    order = Order(
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        customer_phone=payload.customer_phone,
        shipping_address=payload.shipping_address,
        payment_method=payload.payment_method,
        total_amount=payload.total_amount,
        status="pending",
    )
    db.add(order)
    db.flush()  # Get order.id

    # Create items and reduce stock
    for item in payload.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        product.stock -= item.quantity
        db.add(OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        ))

    db.commit()
    # Eager load items for the response
    order = (
        db.query(Order)
        .options(selectinload(Order.items))
        .filter(Order.id == order.id)
        .first()
    )
    return order


@router.get("/", response_model=List[OrderOut])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).options(selectinload(Order.items)).all()
