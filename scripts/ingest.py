import os
import glob
import psycopg2
from dotenv import load_dotenv

# Load .env from project root
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
    print(f"No CSV files found in data/ folder.")
    exit(1)

print(f"Found {len(csv_files)} CSV file(s). Starting import...")

COLUMNS = [
    "event_id", "merchant_id", "event_timestamp", "product",
    "event_type", "amount", "status", "channel", "region", "merchant_tier"
]

total_loaded = 0

for filepath in csv_files:
    filename = os.path.basename(filepath)
    print(f"  Loading {filename}...", end=" ", flush=True)
    try:
        with conn.cursor() as cur, open(filepath, "r", encoding="utf-8") as f:
            next(f)  # skip header
            cur.copy_from(f, "merchant_activities", sep=",", columns=COLUMNS, null="")
            total_loaded += cur.rowcount
            print(f"{cur.rowcount:,} rows.")
    except Exception as e:
        print(f"\n  ⚠️  Skipped {filename}: {e}")

conn.close()
print(f"\n✅ Done! Total rows loaded: {total_loaded:,}")