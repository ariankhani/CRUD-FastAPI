from fastapi import FastAPI

import models
from database.db import Base, engine
from routes import product, user

app = FastAPI()

# Create all tables (in production, use migrations such as Alembic)
Base.metadata.create_all(bind=engine)

# Include the products router
app.include_router(product.router)
app.include_router(user.router)
