from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


# Store schemas
class StoreBase(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None


class StoreCreate(StoreBase):
    pass


class Store(StoreBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# Product schemas
class ProductBase(BaseModel):
    name: str
    code: Optional[str] = None
    category: Optional[str] = None
    purchase_price: Optional[float] = None
    selling_price: Optional[float] = None


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# StoreInventory schemas
class StoreInventoryBase(BaseModel):
    store_id: int
    product_id: int
    current_quantity: int = 0


class StoreInventoryCreate(StoreInventoryBase):
    pass


class StoreInventory(StoreInventoryBase):
    id: int
    updated_at: datetime
    
    # Include related entities
    product: Optional[Product] = None

    class Config:
        orm_mode = True


# StockMovement schemas
class StockMovementBase(BaseModel):
    store_id: int
    product_id: int
    movement_type: str
    quantity: int
    unit_price: Optional[float] = None
    notes: Optional[str] = None

    @validator('movement_type')
    def validate_movement_type(cls, v):
        if v not in ['stock_in', 'sale', 'adjustment']:
            raise ValueError('movement_type must be one of: stock_in, sale, adjustment')
        return v


class StockMovementCreate(StockMovementBase):
    pass


class StockMovement(StockMovementBase):
    id: int
    timestamp: datetime
    
    # Include related entities
    product: Optional[Product] = None

    class Config:
        orm_mode = True


# Reporting schemas
class InventoryReport(BaseModel):
    store_id: int
    store_name: str
    product_count: int
    low_stock_count: int
    total_value: float


class StoreProductInventory(BaseModel):
    product: Product
    current_quantity: int
    updated_at: datetime

    class Config:
        orm_mode = True


class StoreWithInventory(Store):
    inventory: List[StoreProductInventory] = []

    class Config:
        orm_mode = True