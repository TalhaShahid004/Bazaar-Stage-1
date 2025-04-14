# services/inventory/domain/inventory_service.py
from typing import Optional, List
from datetime import datetime
from .models import StockMovement, InventoryLevel
from ..events.publisher import kafka_publish
from ..persistence.repository import InventoryRepository
from ..cache.redis_client import inventory_cache

class InventoryService:
    def __init__(self, repository: InventoryRepository):
        self.repository = repository
    
    async def record_movement(self, movement: StockMovement) -> str:
        """Record a stock movement and update inventory levels."""
        # Validate movement first
        current_level = await self.get_current_level(
            movement.store_id, movement.product_id
        )
        
        # For sales, check if we have enough stock
        if movement.movement_type == "sale" and current_level < movement.quantity:
            raise ValueError("Insufficient stock for this sale")
            
        # Record the movement
        movement_id = await self.repository.save_movement(movement)
        
        # Update inventory level
        new_level = await self._update_inventory_level(movement)
        
        # Publish event to Kafka
        await kafka_publish(
            topic="inventory.movements",
            key=f"{movement.store_id}:{movement.product_id}",
            value={
                "movement_id": movement_id,
                "store_id": movement.store_id,
                "product_id": movement.product_id,
                "movement_type": movement.movement_type,
                "quantity": movement.quantity,
                "timestamp": movement.timestamp,
                "new_level": new_level
            }
        )
        
        # Update cache
        await inventory_cache.set(
            f"inventory:{movement.store_id}:{movement.product_id}",
            new_level,
            expire=3600  # Cache for 1 hour
        )
        
        # Check for low stock and publish alert if needed
        if new_level <= self.get_threshold(movement.product_id):
            await kafka_publish(
                topic="inventory.alerts",
                key=f"{movement.store_id}:{movement.product_id}",
                value={
                    "alert_type": "low_stock",
                    "store_id": movement.store_id,
                    "product_id": movement.product_id,
                    "current_level": new_level,
                    "threshold": self.get_threshold(movement.product_id),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        return movement_id
        
    async def get_current_level(self, store_id: int, product_id: int) -> int:
        """Get current inventory level, with caching."""
        # Try cache first
        cache_key = f"inventory:{store_id}:{product_id}"
        cached_level = await inventory_cache.get(cache_key)
        
        if cached_level is not None:
            return int(cached_level)
            
        # Cache miss, get from database
        level = await self.repository.get_current_level(store_id, product_id)
        
        # Update cache
        await inventory_cache.set(cache_key, level, expire=3600)
        
        return level
    
    async def _update_inventory_level(self, movement: StockMovement) -> int:
        """Update inventory level based on movement type."""
        delta = {
            "stock_in": movement.quantity,
            "sale": -movement.quantity,
            "adjustment": movement.quantity  # Can be positive or negative
        }[movement.movement_type]
        
        return await self.repository.update_level(
            store_id=movement.store_id,
            product_id=movement.product_id,
            delta=delta
        )
    
    def get_threshold(self, product_id: int) -> int:
        """Get low stock threshold for a product."""
        # This could be fetched from product settings
        # For simplicity, using a default
        return 5