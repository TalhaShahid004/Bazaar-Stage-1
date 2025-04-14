# services/analytics/events/consumer.py
import json
import asyncio
from aiokafka import AIOKafkaConsumer
from ..persistence.repository import AnalyticsRepository

class InventoryEventConsumer:
    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository
        self.consumer = None
        
    async def start(self):
        """Start consuming messages from Kafka."""
        self.consumer = AIOKafkaConsumer(
            "inventory.movements",
            bootstrap_servers="kafka:9092",
            group_id="analytics-service",
            value_deserializer=lambda m: json.loads(m.decode("utf-8"))
        )
        
        await self.consumer.start()
        
        try:
            async for message in self.consumer:
                await self.process_message(message)
        finally:
            await self.consumer.stop()
            
    async def process_message(self, message):
        """Process a movement event message."""
        try:
            movement = message.value
            
            # Update daily sales aggregates if it's a sale
            if movement["movement_type"] == "sale":
                await self.repository.update_daily_sales(
                    store_id=movement["store_id"],
                    product_id=movement["product_id"],
                    quantity=movement["quantity"],
                    revenue=movement.get("revenue", 0),
                    timestamp=movement["timestamp"]
                )
                
            # Update current stock level
            await self.repository.update_stock_level(
                store_id=movement["store_id"],
                product_id=movement["product_id"],
                current_level=movement["new_level"]
            )
            
            # Update movement history (for audit/reporting)
            await self.repository.record_movement_history(
                movement_id=movement["movement_id"],
                store_id=movement["store_id"],
                product_id=movement["product_id"],
                movement_type=movement["movement_type"],
                quantity=movement["quantity"],
                timestamp=movement["timestamp"]
            )
            
        except Exception as e:
            # Log error but continue processing messages
            print(f"Error processing message: {e}")
            
# Start consumer when application starts
async def start_consumer():
    repository = AnalyticsRepository()
    consumer = InventoryEventConsumer(repository)
    await consumer.start()
    
# Use a background task to run the consumer
def start_background_tasks():
    asyncio.create_task(start_consumer())