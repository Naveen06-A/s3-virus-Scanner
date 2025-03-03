import boto3
import os
import subprocess
import logging

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client
s3_client = boto3.client('s3')

# Define bucket names
SOURCE_BUCKET = 'source-bucket12'
PRODUCTION_BUCKET = 'productions-bucket123'
QUARANTINE_BUCKET = 'quarantines-bucket123'

def lambda_handler(event, context):
    try:
        # Extract bucket and file info from the S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        # Download file to Lambda's /tmp directory
        local_path = f'/tmp/{os.path.basename(key)}'
        try:
            s3_client.download_file(bucket, key, local_path)
            logger.info(f"File downloaded to {local_path}")
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            raise

        # Scan the file with ClamAV
        try:
            scan_result = subprocess.run(
                ['/opt/bin/clamscan', '--database=/opt/lib/clamav', local_path],
                capture_output=True,
                text=True
            )
            logger.info(f"Scan result: {scan_result.stdout}")
        except Exception as e:
            logger.error(f"Error scanning file: {e}")
            raise

        # Check scan result
        if 'Infected files: 0' in scan_result.stdout:
            destination_bucket = PRODUCTION_BUCKET
        else:
            destination_bucket = QUARANTINE_BUCKET

        # Upload to appropriate bucket
        try:
            s3_client.upload_file(local_path, destination_bucket, key)
            logger.info(f"File uploaded to {destination_bucket}")
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise

        # Delete from source bucket
        try:
            s3_client.delete_object(Bucket=bucket, Key=key)
            logger.info(f"File deleted from source bucket")
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            raise

        # Clean up /tmp
        os.remove(local_path)

        return {
            'statusCode': 200,
            'body': f'File {key} processed. Moved to {destination_bucket}'
        }

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return {
            'statusCode': 500,
            'body': f'Error processing file: {e}'
        }
