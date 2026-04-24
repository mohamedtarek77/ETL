import boto3
import logging
from io import StringIO

logging.basicConfig(level=logging.INFO)

def load_to_s3(df, bucket, key, endpoint):

    logging.info("Connecting to LocalStack...")

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1"
    )

    try:
        s3.create_bucket(Bucket=bucket)
    except Exception:
        pass

    buffer = StringIO()
    df.to_csv(buffer, index=False)

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=buffer.getvalue()
    )

    logging.info(f"Uploaded to {bucket}/{key}")