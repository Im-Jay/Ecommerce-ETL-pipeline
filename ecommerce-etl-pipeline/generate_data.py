"""
Data Generator for the E-Commerce ETL Pipeline.

Generates realistic sample datasets with intentionally dirty data
for testing the ETL pipeline's cleaning and transformation capabilities.

Dirty data injected:
    - Missing values (~5% of records)
    - Duplicate records (~3% of records)
    - Incorrect date formats (mixed formats)
    - Negative quantities in orders
    - Inconsistent category names (case/spelling variations)
    - Invalid foreign keys (orphan references)

Usage:
    python generate_data.py
"""

import random
import pandas as pd
from faker import Faker
from pathlib import Path
from datetime import datetime, timedelta

# Reproducible randomness
fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

# ── Constants ──────────────────────────────────────────────
NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 200
NUM_ORDERS = 10000

OUTPUT_DIR = Path(__file__).resolve().parent / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Reference Data ─────────────────────────────────────────

CATEGORIES_CLEAN = [
    "Electronics", "Clothing", "Home & Kitchen", "Books",
    "Sports & Outdoors", "Beauty & Health", "Toys & Games",
    "Automotive", "Grocery", "Office Supplies",
]

# Inconsistent variants to inject as dirty data
CATEGORY_VARIANTS = {
    "Electronics":       ["electronics", "ELECTRONICS", "Electronicss", "Electronic"],
    "Clothing":          ["clothing", "CLOTHING", "Clothings", "Apparel"],
    "Home & Kitchen":    ["home & kitchen", "HOME & KITCHEN", "Home&Kitchen", "Home and Kitchen"],
    "Books":             ["books", "BOOKS", "Book"],
    "Sports & Outdoors": ["sports & outdoors", "SPORTS & OUTDOORS", "Sports", "Outdoors"],
    "Beauty & Health":   ["beauty & health", "BEAUTY & HEALTH", "Beauty", "Health & Beauty"],
    "Toys & Games":      ["toys & games", "TOYS & GAMES", "Toys", "Games"],
    "Automotive":        ["automotive", "AUTOMOTIVE", "Auto"],
    "Grocery":           ["grocery", "GROCERY", "Groceries"],
    "Office Supplies":   ["office supplies", "OFFICE SUPPLIES", "Office", "Stationery"],
}

PAYMENT_METHODS = [
    "Credit Card", "Debit Card", "UPI", "Net Banking", "Cash on Delivery",
]

INDIAN_STATES = [
    "Maharashtra", "Karnataka", "Tamil Nadu", "Delhi", "Uttar Pradesh",
    "Gujarat", "Rajasthan", "West Bengal", "Telangana", "Kerala",
    "Madhya Pradesh", "Punjab", "Haryana", "Bihar", "Andhra Pradesh",
]

INDIAN_CITIES = {
    "Maharashtra":    ["Mumbai", "Pune", "Nagpur", "Nashik"],
    "Karnataka":      ["Bangalore", "Mysore", "Mangalore", "Hubli"],
    "Tamil Nadu":     ["Chennai", "Coimbatore", "Madurai", "Salem"],
    "Delhi":          ["New Delhi", "Delhi"],
    "Uttar Pradesh":  ["Lucknow", "Noida", "Agra", "Varanasi"],
    "Gujarat":        ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
    "Rajasthan":      ["Jaipur", "Jodhpur", "Udaipur", "Ajmer"],
    "West Bengal":    ["Kolkata", "Howrah", "Durgapur", "Siliguri"],
    "Telangana":      ["Hyderabad", "Warangal", "Nizamabad"],
    "Kerala":         ["Kochi", "Trivandrum", "Calicut", "Thrissur"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur"],
    "Punjab":         ["Chandigarh", "Ludhiana", "Amritsar", "Jalandhar"],
    "Haryana":        ["Gurgaon", "Faridabad", "Panipat", "Karnal"],
    "Bihar":          ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur"],
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Tirupati", "Guntur"],
}

# Realistic product names per category (20 each = 200 total)
PRODUCT_NAMES = {
    "Electronics": [
        "Wireless Earbuds", "Bluetooth Speaker", "Laptop Stand", "USB-C Hub",
        "Webcam HD", "Mechanical Keyboard", "Gaming Mouse", "Monitor Arm",
        "Power Bank 20000mAh", "Smart Watch", "Tablet 10-inch", "Phone Case",
        "HDMI Cable 2m", "Wireless Charger", "LED Desk Lamp",
        "Noise Cancelling Headphones", "Portable SSD 1TB", "WiFi Router",
        "Smart Plug", "Action Camera 4K",
    ],
    "Clothing": [
        "Cotton T-Shirt", "Denim Jeans", "Formal Shirt", "Hoodie",
        "Track Pants", "Polo Shirt", "Kurta", "Winter Jacket",
        "Cargo Shorts", "Blazer", "Wool Sweater", "Cargo Pants",
        "Sweatshirt", "Chinos", "Raincoat",
        "Ethnic Wear", "Running Shoes", "Casual Sneakers",
        "Leather Sandals", "High-Top Sneakers",
    ],
    "Home & Kitchen": [
        "Non-Stick Pan", "Pressure Cooker 5L", "Mixer Grinder", "Water Bottle",
        "Lunch Box Set", "Cutting Board", "Kitchen Knife Set", "Toaster",
        "Coffee Maker", "Air Fryer", "Dinner Set 24pc", "Glass Set",
        "Storage Container Set", "Baking Tray", "Chef Apron",
        "Dish Rack", "Spice Rack", "Blender",
        "Microwave Cover", "Silicone Oven Mitts",
    ],
    "Books": [
        "Python Programming", "Data Science Handbook", "ML Guide",
        "Web Development Bootcamp", "SQL Mastery", "Clean Code",
        "Design Patterns", "Algorithms & DS", "Operating Systems",
        "Computer Networks", "Digital Marketing", "Business Strategy",
        "Self-Help Guide", "Fiction Bestseller", "History of Computing",
        "AI Fundamentals", "Cloud Computing", "DevOps Handbook",
        "Cyber Security 101", "Blockchain Basics",
    ],
    "Sports & Outdoors": [
        "Yoga Mat 6mm", "Dumbbell Set 10kg", "Resistance Bands", "Jump Rope",
        "Tennis Racket", "Cricket Bat", "Football Size 5", "Badminton Set",
        "Cycling Gloves", "Sports Water Bottle", "Gym Bag", "Running Shoes Pro",
        "Swimming Goggles", "Camping Tent 4P", "Hiking Backpack 50L",
        "Fitness Tracker Band", "Exercise Ball 65cm", "Pull-Up Bar",
        "Skateboard", "Fishing Rod",
    ],
    "Beauty & Health": [
        "Face Wash Gel", "Moisturizer SPF 30", "Sunscreen SPF 50", "Shampoo 500ml",
        "Hair Oil 200ml", "Face Mask Pack", "Body Lotion", "Lip Balm",
        "Perfume 100ml", "Deodorant Spray", "Hand Sanitizer 500ml", "Electric Toothbrush",
        "Vitamin Supplements", "First Aid Kit", "Digital Thermometer",
        "Eye Cream", "Hair Dryer 2000W", "Beard Trimmer",
        "Manicure Kit", "Massage Gun",
    ],
    "Toys & Games": [
        "Board Game Classic", "Puzzle 1000pc", "Building Blocks 500pc", "RC Car",
        "Card Game Pack", "Chess Set Wooden", "Rubik's Cube", "Mini Drone",
        "Action Figure Set", "Stuffed Bear", "Science Kit", "Art Supplies Set",
        "Lego Architecture", "Play Dough Set", "Nerf Blaster",
        "Magic Trick Kit", "Electric Train Set", "Dollhouse",
        "Kite Large", "Bubble Machine",
    ],
    "Automotive": [
        "Car Phone Mount", "Dash Cam 1080p", "Seat Cover Set", "Car Air Freshener",
        "Tyre Inflator", "Jump Starter Kit", "Car Vacuum Cleaner", "Sun Shade",
        "Floor Mats Set", "Steering Wheel Cover", "LED Headlight Bulbs", "Car USB Charger",
        "Tool Kit Auto 48pc", "Wiper Blades", "Car Polish Kit",
        "Parking Sensor", "GPS Navigator", "Roof Rack",
        "Bike Cover", "Helmet Full-Face",
    ],
    "Grocery": [
        "Basmati Rice 5kg", "Olive Oil 1L", "Green Tea 100 bags", "Protein Bar 12-pack",
        "Almonds 500g", "Dark Chocolate 70%", "Organic Honey 500g", "Oats 1kg",
        "Peanut Butter 1kg", "Quinoa 1kg", "Chia Seeds 250g", "Coconut Water 12-pack",
        "Instant Noodles 10-pack", "Energy Drink 6-pack", "Granola Mix 750g",
        "Mixed Nuts 1kg", "Coffee Beans 500g", "Herbal Tea Box",
        "Dried Fruits 500g", "Pasta Pack 2kg",
    ],
    "Office Supplies": [
        "Notebook A5 5-pack", "Gel Pens Set 10", "Desk Organizer", "Sticky Notes 12-pack",
        "Stapler Heavy Duty", "Paper Shredder", "Filing Cabinet", "Whiteboard Markers 8",
        "Binder Clips 100", "Scissors Set", "Tape Dispenser", "Scientific Calculator",
        "Envelope Pack 100", "Printer Paper A4", "Highlighter Set 6",
        "Rubber Bands Box", "Paper Weight Glass", "Stamp Pad",
        "Desk Calendar 2025", "Name Badge Holders",
    ],
}


def generate_date(start_year: int = 2022, end_year: int = 2025, dirty: bool = False) -> str:
    """
    Generate a date string, optionally in an incorrect format.

    Args:
        start_year: Earliest year for the date range
        end_year: Latest year for the date range
        dirty: If True, return a date in a non-standard format

    Returns:
        Date string in standard or dirty format
    """
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    date = start + timedelta(days=random.randint(0, (end - start).days))

    if dirty:
        fmt = random.choice([
            "%d/%m/%Y",       # DD/MM/YYYY
            "%m-%d-%Y",       # MM-DD-YYYY
            "%d-%m-%Y",       # DD-MM-YYYY
            "%Y/%m/%d",       # YYYY/MM/DD
            "%B %d, %Y",     # January 15, 2024
        ])
        return date.strftime(fmt)
    return date.strftime("%Y-%m-%d")


def generate_customers() -> pd.DataFrame:
    """Generate 1,000+ customer records with intentional dirty data."""
    print("  Generating customers...")
    customers = []

    for i in range(1, NUM_CUSTOMERS + 1):
        state = random.choice(INDIAN_STATES)
        city = random.choice(INDIAN_CITIES[state])

        customers.append({
            "customer_id": f"CUST_{i:04d}",
            "customer_name": fake.name(),
            "email": fake.email(),
            "city": city,
            "state": state,
            "registration_date": generate_date(2020, 2024),
        })

    # ── Inject dirty data ──────────────────────────────────
    # Missing values (~5%)
    for _ in range(50):
        idx = random.randint(0, len(customers) - 1)
        field = random.choice(["customer_name", "email", "city", "state"])
        customers[idx][field] = random.choice(["", None, "N/A", "null"])

    # Duplicate records (~3%)
    for _ in range(30):
        idx = random.randint(0, len(customers) - 1)
        customers.append(customers[idx].copy())

    # Incorrect date formats (~5%)
    for _ in range(50):
        idx = random.randint(0, len(customers) - 1)
        customers[idx]["registration_date"] = generate_date(2020, 2024, dirty=True)

    random.shuffle(customers)

    df = pd.DataFrame(customers)
    df.to_csv(OUTPUT_DIR / "customers.csv", index=False)
    print(f"    → Generated {len(customers):,} customer records (incl. dirty data)")
    return df


def generate_products() -> pd.DataFrame:
    """Generate 200+ product records with intentional dirty data."""
    print("  Generating products...")
    products = []
    product_id = 1

    for category, names in PRODUCT_NAMES.items():
        for name in names:
            # 15% chance of using a dirty category variant
            if random.random() < 0.15:
                cat = random.choice(CATEGORY_VARIANTS[category])
            else:
                cat = category

            products.append({
                "product_id": f"PROD_{product_id:03d}",
                "product_name": name,
                "category": cat,
                "price": round(random.uniform(99, 9999), 2),
            })
            product_id += 1

    # ── Inject dirty data ──────────────────────────────────
    # Missing values
    for _ in range(10):
        idx = random.randint(0, len(products) - 1)
        field = random.choice(["product_name", "category", "price"])
        products[idx][field] = "" if field != "price" else None

    # Duplicate records
    for _ in range(6):
        idx = random.randint(0, len(products) - 1)
        products.append(products[idx].copy())

    random.shuffle(products)

    df = pd.DataFrame(products)
    df.to_csv(OUTPUT_DIR / "products.csv", index=False)
    print(f"    → Generated {len(products):,} product records (incl. dirty data)")
    return df


def generate_orders(customers_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    """Generate 10,000+ order records with intentional dirty data."""
    print("  Generating orders...")

    customer_ids = [cid for cid in customers_df["customer_id"].dropna().unique()
                    if cid and str(cid).startswith("CUST_")]
    product_ids = [pid for pid in products_df["product_id"].dropna().unique()
                   if pid and str(pid).startswith("PROD_")]

    orders = []

    for i in range(1, NUM_ORDERS + 1):
        orders.append({
            "order_id": f"ORD_{i:05d}",
            "customer_id": random.choice(customer_ids),
            "product_id": random.choice(product_ids),
            "quantity": random.randint(1, 10),
            "order_date": generate_date(2023, 2025),
            "payment_method": random.choice(PAYMENT_METHODS),
        })

    # ── Inject dirty data ──────────────────────────────────
    # Missing values (~5%)
    for _ in range(500):
        idx = random.randint(0, len(orders) - 1)
        field = random.choice(["customer_id", "product_id", "quantity", "payment_method"])
        orders[idx][field] = random.choice(["", None, "N/A"])

    # Negative quantities (~2%)
    for _ in range(200):
        idx = random.randint(0, len(orders) - 1)
        orders[idx]["quantity"] = random.randint(-10, -1)

    # Incorrect date formats (~5%)
    for _ in range(500):
        idx = random.randint(0, len(orders) - 1)
        orders[idx]["order_date"] = generate_date(2023, 2025, dirty=True)

    # Duplicate records (~3%)
    for _ in range(300):
        idx = random.randint(0, len(orders) - 1)
        orders.append(orders[idx].copy())

    # Invalid foreign keys (~1%)
    for _ in range(100):
        idx = random.randint(0, len(orders) - 1)
        orders[idx]["customer_id"] = "CUST_9999"
    for _ in range(100):
        idx = random.randint(0, len(orders) - 1)
        orders[idx]["product_id"] = "PROD_999"

    random.shuffle(orders)

    df = pd.DataFrame(orders)
    df.to_csv(OUTPUT_DIR / "orders.csv", index=False)
    print(f"    → Generated {len(orders):,} order records (incl. dirty data)")
    return df


def main():
    """Generate all sample datasets."""
    print()
    print("=" * 60)
    print("  E-Commerce Sample Data Generator")
    print("=" * 60)
    print()

    customers_df = generate_customers()
    products_df = generate_products()
    generate_orders(customers_df, products_df)

    print()
    print("=" * 60)
    print(f"  ✓ Data generation complete!")
    print(f"  Output directory: {OUTPUT_DIR}")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
