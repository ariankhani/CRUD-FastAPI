from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database.db import Base, engine
from app.routes import orders, product, user

app = FastAPI()

# Configure CORS
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all tables (in production, use migrations such as Alembic)
Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the routers
app.include_router(product.router)
app.include_router(user.router)
app.include_router(orders.router)
