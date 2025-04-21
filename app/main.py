from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database.db import Base, engine
from app.routes import orders, product, user

app = FastAPI()

# Create all tables (in production, use migrations such as Alembic)
Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the products router
app.include_router(product.router)
app.include_router(orders.router)
app.include_router(user.router)
