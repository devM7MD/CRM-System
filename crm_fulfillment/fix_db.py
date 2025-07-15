import os
import django
import sqlite3

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_fulfillment.settings')
django.setup()

# Get the database path from Django settings
from django.conf import settings
db_path = settings.DATABASES['default']['NAME']

print(f"Fixing database at: {db_path}")

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the finance_payment table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='finance_payment';")
if not cursor.fetchone():
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

# Check if the finance_orderfees table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='finance_orderfees';")
if not cursor.fetchone():
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

# Update the django_migrations table to mark all finance migrations as applied
cursor.execute("SELECT name FROM django_migrations WHERE app='finance';")
applied_migrations = [row[0] for row in cursor.fetchall()]

# List of expected finance migrations
expected_migrations = [
    '0001_initial',
    '0002_alter_orderpayment_options_and_more',
    '0003_remove_orderpayment_status_orderpayment_amount_and_more',
    '0004_fix_tables'
]

# Add missing migrations
for migration in expected_migrations:
    if migration not in applied_migrations:
        print(f"Marking migration finance.{migration} as applied...")
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, datetime('now'))",
            ('finance', migration)
        )

# Commit changes and close connection
conn.commit()
conn.close()

print("Database fix completed. You can now run migrations again.") 