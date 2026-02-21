import os
import glob
import csv
import psycopg2
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 5432),
    dbname=os.getenv("DB_NAME", "moniepoint"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", ""),
)
conn.autocommit = True

with conn.cursor() as cur:
    print("Creating table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS merchant_activities (
            event_id        TEXT,
            merchant_id     VARCHAR(20),
            event_timestamp TIMESTAMP,
            product         VARCHAR(20),
            event_type      VARCHAR(30),
            amount          NUMERIC(18, 2) DEFAULT 0,
            status          VARCHAR(10),
            channel         VARCHAR(10),
            region          TEXT,
            merchant_tier   VARCHAR(10)
        );
    """)

    print("Creating indexes...")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_status ON merchant_activities(status);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_product_status ON merchant_activities(product, status);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_merchant_status ON merchant_activities(merchant_id, status);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON merchant_activities(event_timestamp);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_kyc ON merchant_activities(product, event_type, status);")

print("Table and indexes ready.")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
csv_files = sorted(glob.glob(os.path.join(DATA_DIR, "activities_*.csv")))

if not csv_files:
    print("No CSV files found in data/ folder.")
    exit(1)

print(f"Found {len(csv_files)} CSV file(s). Starting import...")

COLUMNS = [
    "event_id", "merchant_id", "event_timestamp", "product",
    "event_type", "amount", "status", "channel", "region", "merchant_tier"
]

AMOUNT_INDEX = COLUMNS.index("amount")  # column position of amount

total_loaded = 0
total_skipped = 0

def clean_amount(value):
    """Return 0 if amount is not a valid number."""
    try:
        return str(float(value))
    except (ValueError, TypeError):
        return "0"

for filepath in csv_files:
    filename = os.path.basename(filepath)
    print(f"  Loading {filename}...", end=" ", flush=True)

    rows_loaded = 0
    rows_skipped = 0

    try:
        with conn.cursor() as cur, open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header

            for row in reader:
                # Skip rows that don't have the right number of columns
                if len(row) != len(COLUMNS):
                    rows_skipped += 1
                    continue

                # Clean the amount field
                row[AMOUNT_INDEX] = clean_amount(row[AMOUNT_INDEX])

                try:
                    cur.execute("""
                        INSERT INTO merchant_activities
                            (event_id, merchant_id, event_timestamp, product,
                             event_type, amount, status, channel, region, merchant_tier)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, row)
                    rows_loaded += 1
                except Exception:
                    rows_skipped += 1

        total_loaded += rows_loaded
        total_skipped += rows_skipped
        print(f"{rows_loaded:,} rows loaded, {rows_skipped} skipped.")

    except Exception as e:
        print(f"\n  ⚠️  Could not read {filename}: {e}")

conn.close()
print(f"\n✅ Done! Total rows loaded: {total_loaded:,} | Total skipped: {total_skipped:,}")