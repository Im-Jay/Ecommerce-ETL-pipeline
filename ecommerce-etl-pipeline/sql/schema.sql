-- ============================================================
-- E-Commerce Data Analytics — Database Schema
-- ============================================================
-- Creates normalized tables for customers, products, and orders
-- with primary keys, foreign keys, indexes, and constraints.
--
-- Usage:
--   psql -U postgres -d ecommerce_analytics -f schema.sql
-- ============================================================

-- Drop existing tables (in reverse dependency order)
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;


-- ────────────────────────────────────────────────────────────
-- Customers Table
-- Stores customer profile and registration information.
-- ────────────────────────────────────────────────────────────
CREATE TABLE customers (
    customer_id       VARCHAR(20)  PRIMARY KEY,
    customer_name     VARCHAR(100) NOT NULL,
    email             VARCHAR(150),
    city              VARCHAR(100),
    state             VARCHAR(100),
    registration_date DATE
);

-- Index on state for regional analytics queries
CREATE INDEX idx_customers_state ON customers(state);

-- Index on registration date for cohort analysis
CREATE INDEX idx_customers_reg_date ON customers(registration_date);


-- ────────────────────────────────────────────────────────────
-- Products Table
-- Stores product catalog with pricing and categorization.
-- ────────────────────────────────────────────────────────────
CREATE TABLE products (
    product_id    VARCHAR(20)   PRIMARY KEY,
    product_name  VARCHAR(150)  NOT NULL,
    category      VARCHAR(100)  NOT NULL,
    price         NUMERIC(10,2) NOT NULL CHECK (price > 0)
);

-- Index on category for category-level aggregations
CREATE INDEX idx_products_category ON products(category);


-- ────────────────────────────────────────────────────────────
-- Orders Table
-- Stores individual order transactions with enriched fields.
-- References customers and products via foreign keys.
-- ────────────────────────────────────────────────────────────
CREATE TABLE orders (
    order_id        VARCHAR(20)   PRIMARY KEY,
    customer_id     VARCHAR(20)   NOT NULL REFERENCES customers(customer_id),
    product_id      VARCHAR(20)   NOT NULL REFERENCES products(product_id),
    quantity        INTEGER       NOT NULL CHECK (quantity > 0),
    order_date      DATE          NOT NULL,
    payment_method  VARCHAR(50),
    revenue         NUMERIC(12,2) NOT NULL,
    order_month     INTEGER       NOT NULL CHECK (order_month BETWEEN 1 AND 12),
    order_year      INTEGER       NOT NULL CHECK (order_year BETWEEN 2000 AND 2100)
);

-- Indexes for analytics queries
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_product_id  ON orders(product_id);
CREATE INDEX idx_orders_order_date  ON orders(order_date);
CREATE INDEX idx_orders_year_month  ON orders(order_year, order_month);
CREATE INDEX idx_orders_payment     ON orders(payment_method);
