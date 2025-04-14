# Bazaar Inventory Tracking System

A scalable inventory management solution for kiryana stores that evolves from a single store to thousands of stores.

## What Is This?

This is my solution to the Bazaar Technologies Engineering challenge. I've designed an inventory system that starts simple and scales up through three stages:

- **Stage 1:** Single store inventory tracking
- **Stage 2:** Support for 500+ stores with central product catalog
- **Stage 3:** Scalable system for thousands of stores with real-time sync

## Project Structure

```
bazaar-inventory/
├── Stage-1/   # Single store with local storage
├── Stage-2/   # Multi-store with centralized database
└── Stage-3/   # Distributed system for thousands of stores
```

## Stage 1: Single Store

A desktop application that helps a single kiryana store track inventory.

- Product management and stock tracking
- Sales recording and daily reports
- Low stock alerts
- Works offline with local database

[See Stage 1 Details](./Stage-1/README.md)

## Stage 2: Multiple Stores

A web-based system that supports hundreds of stores with a central product catalog.

- REST API for inventory operations
- Web interface for all devices
- Store-specific inventory tracking
- Basic security and rate limiting

[See Stage 2 Details](./Stage-2/README.md)

## Stage 3: Enterprise Scale

A distributed system designed to handle thousands of stores with concurrent operations.

- Microservices for independent scaling
- Event-driven design for real-time updates
- Performance optimizations with caching
- Comprehensive audit logging

[See Stage 3 Details](./Stage-3/README.md)

## Technology Evolution

The system evolves through these technologies:

1. **Stage 1:** Python, SQLite, Tkinter
2. **Stage 2:** FastAPI, PostgreSQL, Bootstrap frontend
3. **Stage 3:** Microservices, Kafka, Redis, Kubernetes

## Key Features Across All Stages

- Product inventory tracking
- Recording stock arrivals and sales
- Inventory adjustments
- Low stock alerts
- Reporting and analytics

Each stage maintains these core features while adding capabilities to handle increased scale.

## Running the Project

Each stage has its own setup instructions in its README file.