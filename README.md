# Kiryana Store Inventory System

A straightforward inventory management system built for kiryana stores, designed with simplicity and practicality in mind.

## Overview

Running a kiryana store involves managing hundreds of products, tracking sales, and maintaining appropriate stock levels. This application provides a simple solution to these challenges without requiring technical expertise.

## Key Features

The system focuses on the essential needs of a kiryana store. It provides inventory tracking with visual low-stock alerts and a simple interface for recording sales and stock deliveries. Store owners can view daily performance reports to track business health and create one-click backups to protect their data. The system works offline for areas with unreliable internet.

![features](https://github.com/user-attachments/assets/c5b4731d-bb2e-4af5-ba24-7333582a22ad)


## Installation

To install and run the system:

```
# 1. Make sure Python 3.6+ is installed

# 2. Install required packages
pip install tk
pip install tkcalendar
pip install colorama
pip install tabulate

# 3. Download the application files

# 4. Run the application
python main.py
```

## Why I Built It This Way

Kiryana store owners are busy people who need practical tools. It is a high volume, cash heavy environment. They can have 100s-1000s of daily household items. I designed this system for frequent small transactions, diverse inventory, and owners who need clear reports at a glance.

The database is locally stored, barring any connectivity issues. The system is simple, allowing for bare functionality without unnecessary complex features, easy to operate with minimal keystrokes.

## Data Structure

The system uses a simple approach where all inventory changes (sales, deliveries, adjustments) are recorded as movements, creating a reliable audit trail and making it impossible to lose track of inventory.



