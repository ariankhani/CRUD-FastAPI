from fastapi import FastAPI
from sqlalchemy.orm import declarative_base

from database.db import engine

# from models.product import Base
# from models.users import Base
from routes import product, user

Base = declarative_base()

app = FastAPI()

# Create all tables (in production, use migrations such as Alembic)
Base.metadata.create_all(bind=engine)

# Include the products router
app.include_router(product.router)
app.include_router(user.router)
