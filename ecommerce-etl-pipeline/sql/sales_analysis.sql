-- ============================================================
-- E-Commerce Data Analytics — SQL Analysis Queries
-- ============================================================
-- 10 business analytics queries for sales trends, customer
-- behavior, and product performance analysis.
--
-- Each query is self-contained and can be run independently.
-- ============================================================


-- ────────────────────────────────────────────────────────────
-- 1. MONTHLY REVENUE TREND
-- Purpose: Track revenue over time to identify seasonal patterns
--          and growth trends across months. Useful for forecasting
--          and budget planning.
-- ────────────────────────────────────────────────────────────
SELECT
    order_year                          AS year,
    order_month                         AS month,
    COUNT(order_id)                     AS total_orders,
    SUM(revenue)                        AS total_revenue,
    ROUND(AVG(revenue), 2)              AS avg_order_revenue,
    SUM(quantity)                        AS total_units_sold
FROM orders
GROUP BY order_year, order_month
ORDER BY order_year, order_month;


-- ────────────────────────────────────────────────────────────
-- 2. TOP 10 SELLING PRODUCTS
-- Purpose: Identify the best-selling products by total revenue
--          generated. Helps prioritize inventory and marketing
--          for high-performing products.
-- ────────────────────────────────────────────────────────────
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.price                              AS unit_price,
    SUM(o.quantity)                       AS total_quantity_sold,
    SUM(o.revenue)                       AS total_revenue,
    COUNT(o.order_id)                    AS total_orders
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.price
ORDER BY total_revenue DESC
LIMIT 10;


-- ────────────────────────────────────────────────────────────
-- 3. TOP CUSTOMERS BY REVENUE
-- Purpose: Identify the highest-value customers based on their
--          total spending. Supports targeted marketing, loyalty
--          programs, and VIP customer identification.
-- ────────────────────────────────────────────────────────────
SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    c.state,
    COUNT(o.order_id)                    AS total_orders,
    SUM(o.revenue)                       AS total_spent,
    ROUND(AVG(o.revenue), 2)             AS avg_order_value,
    MIN(o.order_date)                    AS first_purchase,
    MAX(o.order_date)                    AS last_purchase
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.city, c.state
ORDER BY total_spent DESC
LIMIT 15;


-- ────────────────────────────────────────────────────────────
-- 4. REVENUE BY CATEGORY
-- Purpose: Analyze revenue distribution across product categories
--          to identify the most profitable segments and inform
--          strategic product mix decisions.
-- ────────────────────────────────────────────────────────────
SELECT
    p.category,
    COUNT(DISTINCT p.product_id)         AS total_products,
    COUNT(o.order_id)                    AS total_orders,
    SUM(o.quantity)                      AS total_quantity_sold,
    SUM(o.revenue)                       AS total_revenue,
    ROUND(AVG(o.revenue), 2)             AS avg_order_value,
    ROUND(
        SUM(o.revenue) * 100.0 / (SELECT SUM(revenue) FROM orders), 2
    )                                    AS revenue_share_pct
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;


-- ────────────────────────────────────────────────────────────
-- 5. AVERAGE ORDER VALUE
-- Purpose: Calculate overall order value statistics to understand
--          spending patterns and set pricing benchmarks.
-- ────────────────────────────────────────────────────────────
SELECT
    COUNT(order_id)                      AS total_orders,
    SUM(revenue)                         AS total_revenue,
    ROUND(AVG(revenue), 2)               AS avg_order_value,
    ROUND(MIN(revenue), 2)               AS min_order_value,
    ROUND(MAX(revenue), 2)               AS max_order_value,
    ROUND(STDDEV(revenue), 2)            AS stddev_order_value,
    ROUND(
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY revenue), 2
    )                                    AS median_order_value
FROM orders;


-- ────────────────────────────────────────────────────────────
-- 6. ORDERS PER MONTH
-- Purpose: Track order volume over time to understand demand
--          patterns, plan inventory, and allocate resources
--          for peak and off-peak periods.
-- ────────────────────────────────────────────────────────────
SELECT
    order_year                           AS year,
    order_month                          AS month,
    COUNT(order_id)                      AS order_count,
    SUM(quantity)                        AS total_items_sold,
    COUNT(DISTINCT customer_id)          AS unique_customers,
    ROUND(
        COUNT(order_id)::NUMERIC / COUNT(DISTINCT customer_id), 2
    )                                    AS orders_per_customer
FROM orders
GROUP BY order_year, order_month
ORDER BY order_year, order_month;


-- ────────────────────────────────────────────────────────────
-- 7. BEST PERFORMING CATEGORIES
-- Purpose: Rank categories by multiple performance metrics
--          including revenue, order count, and average price.
--          Provides a holistic view of category health.
-- ────────────────────────────────────────────────────────────
SELECT
    p.category,
    SUM(o.revenue)                       AS total_revenue,
    COUNT(o.order_id)                    AS order_count,
    SUM(o.quantity)                      AS units_sold,
    ROUND(AVG(p.price), 2)              AS avg_product_price,
    ROUND(
        SUM(o.revenue) / NULLIF(COUNT(o.order_id), 0), 2
    )                                    AS revenue_per_order,
    RANK() OVER (ORDER BY SUM(o.revenue) DESC)
                                         AS revenue_rank
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;


-- ────────────────────────────────────────────────────────────
-- 8. MOST POPULAR PAYMENT METHOD
-- Purpose: Understand customer payment preferences to optimize
--          checkout experience and negotiate better payment
--          gateway rates.
-- ────────────────────────────────────────────────────────────
SELECT
    payment_method,
    COUNT(order_id)                      AS total_orders,
    SUM(revenue)                         AS total_revenue,
    ROUND(AVG(revenue), 2)              AS avg_order_value,
    ROUND(
        COUNT(order_id) * 100.0 / (SELECT COUNT(*) FROM orders), 2
    )                                    AS usage_pct
FROM orders
GROUP BY payment_method
ORDER BY total_orders DESC;


-- ────────────────────────────────────────────────────────────
-- 9. CUSTOMER LIFETIME VALUE (CLV)
-- Purpose: Calculate the total value each customer brings over
--          their entire relationship. Identifies high-LTV
--          customers for retention strategies.
-- ────────────────────────────────────────────────────────────
SELECT
    c.customer_id,
    c.customer_name,
    c.state,
    c.registration_date,
    COUNT(o.order_id)                    AS total_orders,
    SUM(o.revenue)                       AS lifetime_value,
    ROUND(AVG(o.revenue), 2)            AS avg_order_value,
    MIN(o.order_date)                    AS first_order,
    MAX(o.order_date)                    AS last_order,
    (MAX(o.order_date) - MIN(o.order_date))
                                         AS customer_tenure_days
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name, c.state, c.registration_date
HAVING COUNT(o.order_id) >= 2
ORDER BY lifetime_value DESC
LIMIT 20;


-- ────────────────────────────────────────────────────────────
-- 10. PRODUCT PERFORMANCE ANALYSIS
-- Purpose: Comprehensive product analysis combining sales volume,
--          revenue, and ranking within each category. Identifies
--          underperformers and category leaders.
-- ────────────────────────────────────────────────────────────
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.price                              AS unit_price,
    COALESCE(COUNT(o.order_id), 0)       AS times_ordered,
    COALESCE(SUM(o.quantity), 0)         AS total_units_sold,
    COALESCE(SUM(o.revenue), 0)          AS total_revenue,
    ROUND(AVG(o.quantity), 1)            AS avg_quantity_per_order,
    DENSE_RANK() OVER (
        PARTITION BY p.category
        ORDER BY COALESCE(SUM(o.revenue), 0) DESC
    )                                    AS category_rank
FROM products p
LEFT JOIN orders o ON p.product_id = o.product_id
GROUP BY p.product_id, p.product_name, p.category, p.price
ORDER BY p.category, total_revenue DESC;
