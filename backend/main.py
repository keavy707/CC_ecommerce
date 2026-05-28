from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import products, orders

# Auto-create tables for local dev (use Alembic in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kawaii Atelier API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(orders.router)

@app.get("/")
def root():
    return {"message": "Kawaii Atelier API"}
