from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_remove_orderpayment_status_orderpayment_amount_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL - Make sure tables exist with proper structure
            """
            -- Create django_migrations table if it doesn't exist
            CREATE TABLE IF NOT EXISTS django_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                applied DATETIME NOT NULL
            );
            
            -- Backup existing finance_payment if it exists
            CREATE TABLE IF NOT EXISTS finance_payment_backup AS 
            SELECT * FROM finance_payment WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='finance_payment');
            
            -- Drop finance_payment table if it exists
            DROP TABLE IF EXISTS finance_payment;
            
            -- Check if finance_orderfees exists, if not create it
            CREATE TABLE IF NOT EXISTS finance_orderfees (
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
            
            -- Check if finance_payment exists, if not create it
            CREATE TABLE IF NOT EXISTS finance_payment (
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
            """,
            # Reverse SQL - No-op
            "SELECT 1;"
        ),
    ] 