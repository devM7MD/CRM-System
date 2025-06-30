import sqlite3
import os

# Find the database file by looking in multiple locations
possible_locations = [
    'db.sqlite3',
    '../db.sqlite3',
    '../../db.sqlite3',
    '/e/DcrmProject/db.sqlite3',
    '/e/DcrmProject/crm_fulfillment/db.sqlite3'
]

db_file = None
for location in possible_locations:
    if os.path.exists(location):
        db_file = location
        break

if db_file is None:
    print("Database file not found in any of the expected locations")
    print("Checked:")
    for location in possible_locations:
        print(f"  - {location}")
    exit(1)

print(f"Fixing database: {db_file}")

# Connect to the database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Delete any applied finance migrations
print("Resetting finance migrations...")
cursor.execute("DELETE FROM django_migrations WHERE app='finance'")

# Drop the problematic tables if they exist
print("Dropping existing tables if they exist...")
cursor.execute("DROP TABLE IF EXISTS finance_orderpayment")
cursor.execute("DROP TABLE IF EXISTS finance_orderfees")
cursor.execute("DROP TABLE IF EXISTS finance_payment")

# Create the finance_payment table
print("Creating finance_payment table...")
cursor.execute("""
CREATE TABLE finance_payment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders_order(id) ON DELETE CASCADE,
    payment_method VARCHAR(20) NOT NULL,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    payment_date DATETIME NOT NULL,
    created_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    transaction_id VARCHAR(100) DEFAULT '',
    notes TEXT DEFAULT ''
);
""")

# Create the finance_orderfees table
print("Creating finance_orderfees table...")
cursor.execute("""
CREATE TABLE finance_orderfees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL UNIQUE REFERENCES orders_order(id) ON DELETE CASCADE,
    upsell_fees DECIMAL(10, 2) NOT NULL DEFAULT 0,
    confirmation_fees DECIMAL(10, 2) NOT NULL DEFAULT 0,
    cancellation_fees DECIMAL(10, 2) NOT NULL DEFAULT 0,
    fulfillment_fees DECIMAL(10, 2) NOT NULL DEFAULT 0,
    shipping_fees DECIMAL(10, 2) NOT NULL DEFAULT 0,
    return_fees DECIMAL(10, 2) NOT NULL DEFAULT 0,
    warehouse_fees DECIMAL(10, 2) NOT NULL DEFAULT 0
);
""")

# Mark all migrations as applied
print("Marking migrations as applied...")
migrations = [
    "0001_initial",
    "0002_alter_orderpayment_options_and_more",
    "0003_remove_orderpayment_status_orderpayment_amount_and_more",
    "0004_fix_tables"
]

for migration in migrations:
    cursor.execute(
        "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, datetime('now'))",
        ('finance', migration)
    )

# Commit and close
conn.commit()
conn.close()

print("Database fix completed successfully. You can now run migrations.")
print("Run: python manage.py migrate --fake finance")
print("Then: python manage.py migrate") 