from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Store(Base):
    """Store model for tracking multiple kiryana stores."""
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)
    address = Column(String)
    phone = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    inventory = relationship("StoreInventory", back_populates="store")
    movements = relationship("StockMovement", back_populates="store")


class Product(Base):
    """Product model for the central product catalog."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True)
    category = Column(String, index=True)
    purchase_price = Column(Float)
    selling_price = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    inventory = relationship("StoreInventory", back_populates="product")
    movements = relationship("StockMovement", back_populates="product")


class StoreInventory(Base):
    """Store-specific inventory model to track quantities per store."""
    __tablename__ = "store_inventory"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    current_quantity = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    store = relationship("Store", back_populates="inventory")
    product = relationship("Product", back_populates="inventory")
    
    # Ensure store+product combination is unique
    __table_args__ = (
        UniqueConstraint('store_id', 'product_id', name='unique_store_product'),
    )


class StockMovement(Base):
    """Stock movement model for tracking all inventory changes."""
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    movement_type = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float)
    notes = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    store = relationship("Store", back_populates="movements")
    product = relationship("Product", back_populates="movements")
    
    # Ensure movement_type is valid
    __table_args__ = (
        CheckConstraint(
            movement_type.in_(['stock_in', 'sale', 'adjustment']), 
            name='valid_movement_type'
        ),
    )