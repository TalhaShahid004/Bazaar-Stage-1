# Kiryana Inventory System - Stage 2

A multi-store inventory management system built for kiryana stores, capable of supporting 500+ stores with a central product catalog. This is a Stage 2 enhancement of the original single-store solution.

## Overview

This project extends the original Kiryana Store Inventory System to support multiple stores, adding a REST API for accessing inventory data, centralized product catalog, store-specific inventory tracking, and enhanced reporting capabilities.

## Key Features

- Central product catalog management
- Store-specific inventory tracking
- Real-time stock movement recording (stock-in, sales, adjustments)
- Low stock alerts and notifications
- Filtering and reporting by store and date range
- Basic authentication with API keys
- Request rate limiting to prevent abuse
- Web-based user interface for easy access

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: API Key-based authentication
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Containerization**: Docker & Docker Compose

## System Requirements

- Docker and Docker Compose
- Web browser with JavaScript enabled

## Installation and Setup

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
   Open your browser and navigate to `http://localhost:8080`

4. Use the following default API keys for testing:
   - Store 1: `store1_api_key`
   - Store 2: `store2_api_key`

## API Documentation

Once the application is running, you can access the API documentation at:
`http://localhost:8000/docs`

### Key API Endpoints:

- `/products/` - Manage product catalog
- `/stores/` - Manage store information
- `/inventory/` - View and update inventory levels
- `/movements/` - Record stock movements
- `/reports/` - Generate reports and analytics

## Project Structure

```
kiryana-inventory-system/
│
├── backend/               # FastAPI application
│   ├── app.py             # Main application file
│   ├── models.py          # Database models
│   ├── schemas.py         # Pydantic schemas
│   ├── database.py        # Database connection
│   ├── auth.py            # Authentication logic
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Backend container definition
│
├── frontend/              # Web interface
│   ├── index.html         # Main HTML file
│   ├── styles.css         # CSS styles
│   ├── api.js             # API client
│   └── app.js             # Application logic
│
├── docker-compose.yml     # Docker Compose configuration
└── README.md              # Project documentation
```

## Design Decisions

This implementation focuses on:

1. **Simplicity**: Clean, straightforward code structure for a proof of concept
2. **Scalability**: PostgreSQL database to support 500+ stores
3. **Usability**: Intuitive web interface for managing inventory
4. **Performance**: Efficient queries and indexing for quick access
5. **Security**: Basic authentication and rate limiting

## Future Enhancements (Stage 3)

- Microservices architecture for horizontal scaling
- Event-driven architecture for asynchronous processing
- Read/write separation for performance optimization
- Caching layer for frequently accessed data
- Enhanced security with JWT authentication
- Advanced reporting and analytics
- Mobile application support

## License

MIT License - See LICENSE file for details.