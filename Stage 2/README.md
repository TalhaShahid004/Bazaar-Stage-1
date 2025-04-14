# Kiryana Inventory System - Stage 2

A multi-store inventory management system for kiryana stores, supporting 500+ stores with a central product catalog.

## Project Overview

This system started as a single-store solution and has grown into a multi-store platform that helps kiryana stores manage inventory. Store owners can track products, check stock levels, record sales, and get reports across multiple locations while keeping a central product catalog.

The system tracks stock movements in real-time, sends low stock alerts, and generates reports to help store owners make better inventory decisions.

## Why This Design?

### For Non-Technical Readers

I built this system to be simple and practical. The web interface works on any device with a browser - no special software needed. Having one central product list keeps things consistent, but each store still manages its own inventory.

The dashboard shows important inventory info at a glance and highlights items running low. The reports help owners understand sales patterns and inventory value to make smarter business choices.

I added basic security with API keys so only authorized people can access store data, plus rate limiting to prevent system overload.

### For Technical Readers

My design choices were based on needing to support 500+ stores while keeping a good balance of features, performance, and simplicity for this proof-of-concept.

#### Backend Architecture

I picked FastAPI for my backend because it:
- Performs well with async support
- Has built-in API documentation
- Uses type annotations for better code quality
- Can be deployed to production easily

PostgreSQL made sense as the database because it has:
- Strong ACID compliance for data integrity
- Good handling of concurrent connections
- Solid performance for complex queries
- Clear upgrade path for cloud deployment

Using a central product catalog with store-specific inventory tables gives a good balance of normalization and query performance, making product management efficient while supporting per-store inventory tracking.

#### Frontend Implementation

For the frontend, I kept it straightforward with HTML/CSS/JavaScript and Bootstrap. I chose this approach because it's:
- Simple and quick to develop
- Works on most devices
- Has minimal dependencies
- Uses common tech that's easier to maintain

The JavaScript client talks to the backend through a basic API client that handles authentication and common data operations.

## How It Works

The system is built around four main entities:
1. Products (central catalog)
2. Stores (individual store information)
3. Store Inventory (store-specific stock levels)
4. Stock Movements (record of all inventory changes)

Every inventory change gets recorded as a movement with a specific type (stock in, sale, or adjustment), creating an audit trail while keeping current inventory levels updated.

The REST API has endpoints for managing products, stores, inventory, and recording stock movements, with filtering for reporting.

## Installation and Setup

### Prerequisites
- Docker and Docker Compose
- Web browser with JavaScript enabled

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/TalhaShahid004/Bazaar-Case-Study/Stage-2.git
   cd Bazaar-Case-Study/Stage-2
   ```

2. Start the application using Docker Compose:
   ```
   docker-compose up -d
   ```

3. Access the web interface:
   Open your browser and go to `http://localhost:8080`

4. Use the default API keys for testing:
   - Store 1: `store1_api_key`
   - Store 2: `store2_api_key`

### Project Structure

The project has a clean separation between components:

- `backend/`: The FastAPI application
  - `app.py`: Main application entry point
  - `models.py`: Database models using SQLAlchemy
  - `schemas.py`: Pydantic schemas for validation
  - `database.py`: Database connection management
  - `auth.py`: Authentication and rate limiting logic

- `frontend/`: The web interface
  - `index.html`: Main application page
  - `styles.css`: CSS for styling
  - `api.js`: Client for API communication
  - `app.js`: Frontend application logic

- `docker-compose.yml`: Docker configuration for all services

## API Documentation

When the application is running, you can find the complete API documentation at `http://localhost:8000/docs`, which gives you interactive docs for all endpoints.

Key API endpoints:
- `/products/`: Manage the central product catalog
- `/stores/`: Manage store information
- `/inventory/`: View and update inventory levels
- `/movements/`: Record stock movements (stock in, sales, adjustments)
- `/reports/`: Generate inventory and sales reports

## Future Enhancements (Stage 3)

The current implementation has a solid foundation that can grow to support thousands of stores without major redesign:

- Microservices architecture for horizontal scaling
- Event-driven architecture for async processing
- Read/write separation for better performance
- Caching for frequently accessed data
- Better security with JWT authentication
- More reporting and analytics
- Mobile application support

## License

MIT License - See LICENSE file for details.