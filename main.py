from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session


from shop import Product, ProductCreate, ProductOut, SessionLocal
app = FastAPI()


app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Get all Products
@app.get("/products/", response_model=list[ProductOut])
def show_product(limit: int = 10, skip: int = 0, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

# Get product by id
@app.get("/products/{product_id}", response_model=list[ProductOut])
def product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Update Product
@app.put("/products/update/{product_id}", response_model=ProductOut)
def product_update(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    get_product = db.query(Product).filter(Product.id == product_id).first()
    if not get_product:
        raise HTTPException(status_code=404, detail="Product not found")
    get_product.name = product.name # type: ignore
    get_product.price = product.price # type: ignore
    get_product.image = product.image # type: ignore
    db.commit()
    db.refresh(get_product)
    return get_product


# Delete Product
@app.delete("/products/delete/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"detail": "Product deleted"}



# Create Product
@app.post("/products/create", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(name=product.name, price=product.price, image=product.image)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
