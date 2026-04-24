
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

# Reasonable domain boundaries
MIN_PRICE = 0.01
MAX_PRICE = 10_000
MIN_QTY = 1
MAX_QTY = 1_000
DATE_FLOOR = pd.Timestamp("2020-01-01")
DATE_CEIL  = pd.Timestamp("today").normalize()   # no future dates


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    logging.info("Starting transformation — %d rows incoming", len(df))
    original_count = len(df)
    quarantine = []   # collect rows that were dropped and why

    # ------------------------------------------------------------------ #
    # 1. Dedup
    # ------------------------------------------------------------------ #
    df = df.drop_duplicates()

    # ------------------------------------------------------------------ #
    # 2. price — coerce non-numeric to NaN, then validate range
    # ------------------------------------------------------------------ #
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    bad_price = df["price"].isna() | (df["price"] < MIN_PRICE) | (df["price"] > MAX_PRICE)
    if bad_price.any():
        quarantine.append(df[bad_price].assign(_reason="invalid_price"))
        logging.warning("Dropping %d rows with invalid price", bad_price.sum())
        df = df[~bad_price].copy()

    # ------------------------------------------------------------------ #
    # 3. quantity — coerce, then validate range
    # ------------------------------------------------------------------ #
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

    bad_qty = df["quantity"].isna() | (df["quantity"] < MIN_QTY) | (df["quantity"] > MAX_QTY)
    if bad_qty.any():
        quarantine.append(df[bad_qty].assign(_reason="invalid_quantity"))
        logging.warning("Dropping %d rows with invalid quantity", bad_qty.sum())
        df = df[~bad_qty].copy()

    # ------------------------------------------------------------------ #
    # 4. date — coerce unparseable values, drop NaT / out-of-range dates
    # ------------------------------------------------------------------ #
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    bad_date = (
        df["date"].isna()
        | (df["date"] < DATE_FLOOR)
        | (df["date"] > DATE_CEIL)
    )
    if bad_date.any():
        quarantine.append(df[bad_date].assign(_reason="invalid_date"))
        logging.warning("Dropping %d rows with invalid date", bad_date.sum())
        df = df[~bad_date].copy()

    # ------------------------------------------------------------------ #
    # 5. Derived column — safe now that price & quantity are clean
    # ------------------------------------------------------------------ #
    df["total_value"] = (df["price"] * df["quantity"]).round(2)

    # ------------------------------------------------------------------ #
    # 6. Final type clean-up
    # ------------------------------------------------------------------ #
    df["quantity"] = df["quantity"].astype(int)
    df = df.reset_index(drop=True)

    # ------------------------------------------------------------------ #
    # 7. Summary
    # ------------------------------------------------------------------ #
    removed = original_count - len(df)
    logging.info(
        "Transformation complete — %d clean rows kept, %d rows removed",
        len(df), removed,
    )

    if quarantine:
        quarantine_df = pd.concat(quarantine, ignore_index=True)
        logging.info("Quarantine breakdown:\n%s",
                     quarantine_df["_reason"].value_counts().to_string())

    return df


# --------------------------------------------------------------------------- #
# Optional: expose the quarantine log for callers that want it
# --------------------------------------------------------------------------- #
def transform_data_with_report(df: pd.DataFrame):
    """
    Returns (clean_df, quarantine_df).
    Useful for pipelines that need to audit rejected rows separately.
    """
    original_count = len(df)
    df = df.drop_duplicates()
    quarantine = []

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    bad_price = df["price"].isna() | (df["price"] < MIN_PRICE) | (df["price"] > MAX_PRICE)
    quarantine.append(df[bad_price].assign(_reason="invalid_price"))
    df = df[~bad_price].copy()

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    bad_qty = df["quantity"].isna() | (df["quantity"] < MIN_QTY) | (df["quantity"] > MAX_QTY)
    quarantine.append(df[bad_qty].assign(_reason="invalid_quantity"))
    df = df[~bad_qty].copy()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    bad_date = df["date"].isna() | (df["date"] < DATE_FLOOR) | (df["date"] > DATE_CEIL)
    quarantine.append(df[bad_date].assign(_reason="invalid_date"))
    df = df[~bad_date].copy()

    df["total_value"] = (df["price"] * df["quantity"]).round(2)
    df["quantity"] = df["quantity"].astype(int)
    df = df.reset_index(drop=True)

    quarantine_df = pd.concat(quarantine, ignore_index=True)
    quarantine_df = quarantine_df[quarantine_df["id"].notna()]   # drop empty concat artefacts

    return df, quarantine_df


# import pandas as pd
# import logging

# logging.basicConfig(level=logging.INFO)

# def transform_data(df):
#     logging.info("Transforming data...")

#     df = df.drop_duplicates()

#     df["price"] = df["price"].fillna(0)
#     df["quantity"] = df["quantity"].fillna(0)

#     df["total_price"] = df["price"] * df["quantity"]

#     df["date"] = pd.to_datetime(df["date"])

#     logging.info("Transformation done")
#     return df


