import boto3
import logging

logging.basicConfig(level=logging.INFO)

def explore_s3(bucket="sales-bucket", key="output/sales.csv", endpoint="http://localstack:4566"):

    logging.info("=== Connecting to LocalStack S3 ===")

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1"
    )

    # عرض كل الـ buckets
    logging.info("=== Buckets ===")
    buckets = s3.list_buckets().get("Buckets", [])
    if not buckets:
        logging.info("  No buckets found.")
    for b in buckets:
        logging.info(f"  Bucket: {b['Name']}")

    # عرض محتوى كل bucket
    for b in buckets:
        logging.info(f"=== Files in '{b['Name']}' ===")
        objects = s3.list_objects_v2(Bucket=b["Name"]).get("Contents", [])
        if not objects:
            logging.info("  (empty)")
        for obj in objects:
            logging.info(f"  - {obj['Key']}  ({obj['Size']} bytes)  Last Modified: {obj['LastModified']}")

    # قراءة محتوى الملف
    logging.info(f"=== Reading '{key}' from '{bucket}' ===")
    try:
        file_obj = s3.get_object(Bucket=bucket, Key=key)
        content = file_obj["Body"].read().decode("utf-8")
        lines = content.split("\n")
        for line in lines[:20]:
            logging.info(line)
    except Exception as e:
        logging.warning(f"Could not read file: {e}")