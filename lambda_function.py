import boto3
import os
import subprocess

# Initialize S3 client
s3_client = boto3.client('s3')

# Replace with your bucket names
SOURCE_BUCKET12 = 'source-bucket12'
PRODUCTIONS_BUCKET123 = 'productions-bucket123'
QUARANTINES_BUCKET123 = 'quarantines-bucket123'

def lambda_handler(event, context):
    # Extract bucket and file info from the S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Download file to Lambda's /tmp directory
    local_path = f'/tmp/{os.path.basename(key)}'
    s3_client.download_file(bucket, key, local_path)

    # Scan the file with ClamAV (assumes ClamAV is in Lambda Layer)
    scan_result = subprocess.run(
        ['/opt/bin/clamscan', '--database=/opt/lib/clamav', local_path],
        capture_output=True,
        text=True
    )

    # Check scan result
    if 'Infected files: 0' in scan_result.stdout:
        destination_bucket = PRODUCTIONS_BUCKET123
    else:
        destination_bucket = QUARANTINES_BUCKET123

    # Upload to appropriate bucket
    s3_client.upload_file(local_path, destination_bucket, key)

    # Delete from source bucket
    s3_client.delete_object(Bucket=bucket, Key=key)

    # Clean up /tmp
    os.remove(local_path)

    return {
        'statusCode': 200,
        'body': f'File {key} processed. Moved to {destination_bucket}'
    }