from datetime import datetime, date
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from database import get_db, engine, Base
from models import Product, Store, StoreInventory, StockMovement
import schemas
from auth import rate_limit_middleware

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Kiryana Inventory API")

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limit headers to responses
@app.middleware("http")
async def add_rate_limit_headers(request, call_next):
    response = await call_next(request)
    
    if hasattr(request.state, 'rate_limit'):
        response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)
        response.headers["X-RateLimit-Reset"] = str(request.state.rate_limit_reset)
    
    return response

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Kiryana Inventory API v1"}

# Store endpoints
@app.post("/stores/", response_model=schemas.Store)
def create_store(store: schemas.StoreCreate, db: Session = Depends(get_db), 
                 store_code: str = Depends(rate_limit_middleware)):
    # Check if store with this code already exists
    db_store = db.query(Store).filter(Store.code == store.code).first()
    if db_store:
        raise HTTPException(status_code=400, detail="Store code already registered")
    
    # Create new store
    new_store = Store(**store.dict())
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store


@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int, 
    product: schemas.ProductCreate, 
    db: Session = Depends(get_db),
    store_code: str = Depends(rate_limit_middleware)
):
    # Check if product exists
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if code is being changed and if new code already exists
    if product.code and product.code != db_product.code:
        existing_product = db.query(Product).filter(Product.code == product.code).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="Product code already exists")
    
    # Update product fields
    db_product.name = product.name
    db_product.code = product.code
    db_product.category = product.category
    db_product.purchase_price = product.purchase_price
    db_product.selling_price = product.selling_price
    
    db.commit()
    db.refresh(db_product)
    
    return db_product


@app.get("/stores/", response_model=List[schemas.Store])
def read_stores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               store_code: str = Depends(rate_limit_middleware)):
    stores = db.query(Store).offset(skip).limit(limit).all()
    return stores

@app.get("/stores/{store_id}", response_model=schemas.Store)
def read_store(store_id: int, db: Session = Depends(get_db),
              store_code: str = Depends(rate_limit_middleware)):
    db_store = db.query(Store).filter(Store.id == store_id).first()
    if db_store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return db_store

# Product endpoints
@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db),
                  store_code: str = Depends(rate_limit_middleware)):
    # Check if product code already exists if provided
    if product.code:
        db_product = db.query(Product).filter(Product.code == product.code).first()
        if db_product:
            raise HTTPException(status_code=400, detail="Product code already exists")
    
    # Create new product
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.get("/products/", response_model=List[schemas.Product])
def read_products(
    skip: int = 0, 
    limit: int = 100, 
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    store_code: str = Depends(rate_limit_middleware)
):
    query = db.query(Product)
    
    # Apply category filter
    if category:
        query = query.filter(Product.category == category)
    
    # Apply search filter
    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%") | 
            Product.code.ilike(f"%{search}%")
        )
    
    products = query.offset(skip).limit(limit).all()
    return products

@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db),
                store_code: str = Depends(rate_limit_middleware)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

# Inventory endpoints
@app.get("/inventory/", response_model=List[schemas.StoreInventory])
def read_inventory(
    store_id: Optional[int] = None,
    product_id: Optional[int] = None,
    low_stock: Optional[bool] = False,
    threshold: Optional[int] = 5,
    db: Session = Depends(get_db),
    store_code: str = Depends(rate_limit_middleware)
):
    query = db.query(StoreInventory).join(Product)
    
    # Apply filters
    if store_id:
        query = query.filter(StoreInventory.store_id == store_id)
    
    if product_id:
        query = query.filter(StoreInventory.product_id == product_id)
    
    if low_stock:
        query = query.filter(StoreInventory.current_quantity <= threshold)
    
    # Get results
    inventory_items = query.all()
    return inventory_items

@app.post("/inventory/", response_model=schemas.StoreInventory)
def create_or_update_inventory(
    inventory: schemas.StoreInventoryCreate,
    db: Session = Depends(get_db),
    store_code: str = Depends(rate_limit_middleware)
):
    # Check if store exists
    db_store = db.query(Store).filter(Store.id == inventory.store_id).first()
    if not db_store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Check if product exists
    db_product = db.query(Product).filter(Product.id == inventory.product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if inventory record exists
    db_inventory = db.query(StoreInventory).filter(
        StoreInventory.store_id == inventory.store_id,
        StoreInventory.product_id == inventory.product_id
    ).first()
    
    if db_inventory:
        # Update existing record
        db_inventory.current_quantity = inventory.current_quantity
        db.commit()
        db.refresh(db_inventory)
        return db_inventory
    else:
        # Create new record
        new_inventory = StoreInventory(**inventory.dict())
        db.add(new_inventory)
        db.commit()
        db.refresh(new_inventory)
        return new_inventory

# Stock Movement endpoints
@app.post("/movements/", response_model=schemas.StockMovement)
def create_stock_movement(
    movement: schemas.StockMovementCreate,
    db: Session = Depends(get_db),
    store_code: str = Depends(rate_limit_middleware)
):
    # Check if store exists
    db_store = db.query(Store).filter(Store.id == movement.store_id).first()
    if not db_store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Check if product exists
    db_product = db.query(Product).filter(Product.id == movement.product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create stock movement record
    new_movement = StockMovement(**movement.dict())
    db.add(new_movement)
    
    # Update inventory
    db_inventory = db.query(StoreInventory).filter(
        StoreInventory.store_id == movement.store_id,
        StoreInventory.product_id == movement.product_id
    ).first()
    
    if db_inventory:
        # Update existing inventory
        if movement.movement_type == 'stock_in':
            db_inventory.current_quantity += movement.quantity
        elif movement.movement_type == 'sale':
            if db_inventory.current_quantity < movement.quantity:
                raise HTTPException(status_code=400, detail="Not enough stock")
            db_inventory.current_quantity -= movement.quantity
        elif movement.movement_type == 'adjustment':
            db_inventory.current_quantity += movement.quantity  # Can be negative for removal
    else:
        # Create new inventory record
        if movement.movement_type == 'sale':
            raise HTTPException(status_code=400, detail="Cannot sell product not in inventory")
        
        new_quantity = movement.quantity if movement.movement_type == 'stock_in' else 0
        db_inventory = StoreInventory(
            store_id=movement.store_id,
            product_id=movement.product_id,
            current_quantity=new_quantity
        )
        db.add(db_inventory)
    
    db.commit()
    db.refresh(new_movement)
    return new_movement

@app.get("/movements/", response_model=List[schemas.StockMovement])
def read_movements(
    store_id: Optional[int] = None,
    product_id: Optional[int] = None,
    movement_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    store_code: str = Depends(rate_limit_middleware)
):
    query = db.query(StockMovement)
    
    # Apply filters
    if store_id:
        query = query.filter(StockMovement.store_id == store_id)
    
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    
    if movement_type:
        query = query.filter(StockMovement.movement_type == movement_type)
    
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        query = query.filter(StockMovement.timestamp >= start_datetime)
    
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(StockMovement.timestamp <= end_datetime)
    
    # Order by timestamp descending
    query = query.order_by(StockMovement.timestamp.desc())
    
    movements = query.offset(skip).limit(limit).all()
    return movements

# Reporting endpoint
@app.get("/reports/inventory-summary")
def get_inventory_summary(
    store_id: Optional[int] = None,
    low_stock_threshold: int = 5,
    db: Session = Depends(get_db),
    store_code: str = Depends(rate_limit_middleware)
):
    # Base query for all stores or specific store
    stores_query = db.query(Store)
    if store_id:
        stores_query = stores_query.filter(Store.id == store_id)
    
    stores = stores_query.all()
    result = []
    
    for store in stores:
        # Count products in inventory
        product_count = db.query(func.count(StoreInventory.id))\
            .filter(StoreInventory.store_id == store.id)\
            .scalar()
        
        # Count low stock items
        low_stock_count = db.query(func.count(StoreInventory.id))\
            .filter(
                StoreInventory.store_id == store.id,
                StoreInventory.current_quantity <= low_stock_threshold
            )\
            .scalar()
        
        # Calculate total inventory value
        inventory_value = db.query(func.sum(
            StoreInventory.current_quantity * Product.selling_price
        ))\
            .join(Product)\
            .filter(StoreInventory.store_id == store.id)\
            .scalar() or 0
        
        store_summary = {
            "store_id": store.id,
            "store_name": store.name,
            "product_count": product_count,
            "low_stock_count": low_stock_count,
            "total_value": round(inventory_value, 2)
        }
        
        result.append(store_summary)
    
    return result

@app.get("/reports/daily-sales")
def get_daily_sales(
    store_id: Optional[int] = None,
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db),
    store_code: str = Depends(rate_limit_middleware)
):
    # Determine date range
    if not start_date:
        start_date = date.today()
    
    if not end_date:
        end_date = date.today()
    
    # Convert to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Base filters
    filters = [
        StockMovement.movement_type == 'sale',
        StockMovement.timestamp >= start_datetime,
        StockMovement.timestamp <= end_datetime
    ]
    
    if store_id:
        filters.append(StockMovement.store_id == store_id)
    
    # Get daily sales data
    sales_data = db.query(
        func.date(StockMovement.timestamp).label('date'),
        func.count(StockMovement.id).label('transaction_count'),
        func.sum(StockMovement.quantity).label('total_items'),
        func.sum(StockMovement.quantity * StockMovement.unit_price).label('total_revenue')
    )\
        .filter(and_(*filters))\
        .group_by(func.date(StockMovement.timestamp))\
        .order_by(func.date(StockMovement.timestamp))\
        .all()
    
    # Format results
    result = []
    for date_str, transaction_count, total_items, total_revenue in sales_data:
        result.append({
            "date": date_str.strftime('%Y-%m-%d'),
            "transaction_count": transaction_count,
            "total_items": total_items or 0,
            "total_revenue": round(total_revenue or 0, 2)
        })
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)