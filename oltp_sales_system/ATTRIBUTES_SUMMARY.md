# OLTP Database - Table Attributes Summary

## Overview
This document details all attributes for the OLTP (Online Transaction Processing) database designed to efficiently handle sales transactions and support analytical queries.

---

## 1. CUSTOMER Table

**Purpose**: Store customer information for transaction processing

| Attribute | Data Type | Constraints | Description |
|-----------|-----------|-------------|-------------|
| customer_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each customer |
| first_name | VARCHAR(50) | NOT NULL | Customer's first name |
| last_name | VARCHAR(50) | NOT NULL | Customer's last name |
| email | VARCHAR(100) | NOT NULL, UNIQUE | Customer's email address (unique) |
| phone | VARCHAR(20) | NULL | Customer's contact number |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `customer_id`
- UNIQUE INDEX on `email`

---

## 2. PRODUCT Table

**Purpose**: Store product catalog information

| Attribute | Data Type | Constraints | Description |
|-----------|-----------|-------------|-------------|
| product_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each product |
| product_name | VARCHAR(100) | NOT NULL | Name of the product |
| category | VARCHAR(50) | NOT NULL | Product category (Electronics, Clothing, etc.) |
| brand | VARCHAR(50) | NOT NULL | Brand/manufacturer name |
| unit_price | DECIMAL(10,2) | NOT NULL | Current selling price per unit |
| is_active | BOOLEAN | DEFAULT TRUE | Product availability status |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `product_id`
- INDEX on `category` for filtering
- INDEX on `is_active` for active product queries

---

## 3. LOCATION Table

**Purpose**: Store sales location/store information

| Attribute | Data Type | Constraints | Description |
|-----------|-----------|-------------|-------------|
| location_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each location |
| location_name | VARCHAR(100) | NOT NULL | Name of the store/location |
| city | VARCHAR(50) | NOT NULL | City where location is situated |
| address | VARCHAR(200) | NULL | Complete street address |
| country | VARCHAR(50) | NOT NULL | Country code or name |
| is_active | BOOLEAN | DEFAULT TRUE | Location operational status |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `location_id`
- INDEX on `city` for location-based queries
- INDEX on `country` for regional analysis

---

## 4. SALES Table (Fact Table)

**Purpose**: Store all sales transactions - the core OLTP table

| Attribute | Data Type | Constraints | Description |
|-----------|-----------|-------------|-------------|
| sale_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each sale transaction |
| sale_timestamp | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date and time of the sale |
| quantity | INT | NOT NULL, CHECK (quantity > 0) | Number of units sold |
| unit_price | DECIMAL(10,2) | NOT NULL | Price per unit at time of sale |
| total_amount | DECIMAL(12,2) | NOT NULL | Total transaction amount (quantity × unit_price) |
| customer_id | INT | FOREIGN KEY | Reference to CUSTOMER table |
| product_id | INT | FOREIGN KEY, NOT NULL | Reference to PRODUCT table |
| location_id | INT | FOREIGN KEY, NOT NULL | Reference to LOCATION table |

**Indexes** (Critical for OLTP Performance):
- PRIMARY KEY on `sale_id`
- INDEX on `product_id` (for product-based queries)
- INDEX on `location_id` (for location-based queries)
- INDEX on `sale_timestamp` (for time-based queries)
- COMPOSITE INDEX on `(product_id, location_id, sale_timestamp)` (for Query 1)
- COMPOSITE INDEX on `(product_id, location_id)` (for Query 2)
- FOREIGN KEY on `customer_id` → CUSTOMER(customer_id)
- FOREIGN KEY on `product_id` → PRODUCT(product_id)
- FOREIGN KEY on `location_id` → LOCATION(location_id)

---

## Query Support

### Query 1: Sales for a given product by location over a period of time
**Supported by**:
- Composite index: `(product_id, location_id, sale_timestamp)`
- Individual columns: `product_id`, `location_id`, `sale_timestamp`

### Query 2: Maximum number of sales for a given product over time for a given location
**Supported by**:
- Composite index: `(product_id, location_id)`
- Sale timestamp for time-based aggregation

---

## OLTP Design Principles Applied

1. **Normalization**: All tables are in 3NF to minimize redundancy
2. **Referential Integrity**: Foreign keys ensure data consistency
3. **Audit Trail**: `created_at` and `updated_at` timestamps on all tables
4. **Data Quality**: NOT NULL constraints on critical fields
5. **Performance**: Strategic indexes on columns used in WHERE/JOIN clauses
6. **Flexibility**: `is_active` flags for soft deletes
7. **Scalability**: Auto-increment primary keys for easy insertion
8. **Transaction Support**: Design supports ACID properties
