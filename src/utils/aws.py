import boto3
import os
from botocore.exceptions import ClientError
from src.config import settings

boto3.setup_default_session(profile_name=settings.AWS_PROFILE)


def upload_to_s3(file_path):
    s3_client = boto3.client("s3")
    object_name = os.path.basename(file_path)
    # bucket_name = "txn-invoice" #prod
    bucket_name="moi-temp-2"
    try:
        s3_client.upload_file(file_path, bucket_name, object_name,
        ExtraArgs={'ContentType':'application/pdf','ContentDisposition': 'inline'}
        )
        # Use this code if bucket is private
        # url = s3_client.generate_presigned_url(
        #     ClientMethod="get_object",
        #     Params={"Bucket": "txn-invoice", "Key": object_name},
        #     ExpiresIn=3600 * 24 * 365 * 10,  # 10 years
        # )
        url = f"https://{bucket_name}.s3.ap-south-1.amazonaws.com/{object_name}"
        return url
    except ClientError:
        return None