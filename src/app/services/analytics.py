from src.app.database import get_connection, release_connection

_cache = {}


def _query(sql: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        release_connection(conn)


def get_top_merchant():
    if "top_merchant" in _cache:
        return _cache["top_merchant"]

    rows = _query("""
        SELECT merchant_id, SUM(amount) AS total_volume
        FROM merchant_activities
        WHERE status = 'SUCCESS'
        GROUP BY merchant_id
        ORDER BY total_volume DESC
        LIMIT 1
    """)

    result = {"merchant_id": None, "total_volume": 0.00}
    if rows:
        result = {
            "merchant_id": rows[0][0],
            "total_volume": round(float(rows[0][1]), 2),
        }

    _cache["top_merchant"] = result
    return result


def get_monthly_active_merchants():
    if "monthly_active" in _cache:
        return _cache["monthly_active"]

    rows = _query("""
        SELECT
            TO_CHAR(event_timestamp, 'YYYY-MM') AS month,
            COUNT(DISTINCT merchant_id) AS active_merchants
        FROM merchant_activities
        WHERE status = 'SUCCESS'
        GROUP BY month
        ORDER BY month
    """)

    result = {row[0]: row[1] for row in rows}
    _cache["monthly_active"] = result
    return result


def get_product_adoption():
    if "product_adoption" in _cache:
        return _cache["product_adoption"]

    rows = _query("""
        SELECT product, COUNT(DISTINCT merchant_id) AS merchant_count
        FROM merchant_activities
        GROUP BY product
        ORDER BY merchant_count DESC
    """)

    result = {row[0]: row[1] for row in rows}
    _cache["product_adoption"] = result
    return result


def get_kyc_funnel():
    if "kyc_funnel" in _cache:
        return _cache["kyc_funnel"]

    rows = _query("""
        SELECT event_type, COUNT(DISTINCT merchant_id) AS merchant_count
        FROM merchant_activities
        WHERE product = 'KYC'
          AND status = 'SUCCESS'
          AND event_type IN ('DOCUMENT_SUBMITTED', 'VERIFICATION_COMPLETED', 'TIER_UPGRADE')
        GROUP BY event_type
    """)

    lookup = {row[0]: row[1] for row in rows}
    result = {
        "documents_submitted": lookup.get("DOCUMENT_SUBMITTED", 0),
        "verifications_completed": lookup.get("VERIFICATION_COMPLETED", 0),
        "tier_upgrades": lookup.get("TIER_UPGRADE", 0),
    }

    _cache["kyc_funnel"] = result
    return result


def get_failure_rates():
    if "failure_rates" in _cache:
        return _cache["failure_rates"]

    rows = _query("""
        SELECT
            product,
            ROUND(
                100.0 * SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END)
                / NULLIF(
                    SUM(CASE WHEN status IN ('SUCCESS', 'FAILED') THEN 1 ELSE 0 END),
                    0
                ),
                1
            ) AS failure_rate
        FROM merchant_activities
        WHERE status IN ('SUCCESS', 'FAILED')
        GROUP BY product
        ORDER BY failure_rate DESC
    """)

    result = [
        {
            "product": row[0],
            "failure_rate": float(row[1]) if row[1] is not None else 0.0
        }
        for row in rows
    ]

    _cache["failure_rates"] = result
    return result