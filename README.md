# S3 File Virus Scanning and Management

## Overview
This project uses AWS Lambda, S3, and ClamAV to scan files uploaded to an S3 bucket for viruses, moving clean files to a production bucket and infected files to a quarantine bucket.

## Project Structure
- `lambda_function.py`: Main Lambda code for scanning and moving files.
- `clamav-layer.zip`: Lambda Layer with ClamAV binaries (optional, build if missing).
- `README.md`: This file.
- `requirements.txt`: Python dependencies.

## Setup Instructions
1. **Create S3 Buckets**:
   - Source: `source-bucket`
   - Production: `production-bucket`
   - Quarantine: `quarantine-bucket`
2. **Build ClamAV Layer** (if `clamav-layer.zip` is missing):
   - Use a Linux environment (e.g., EC2).
   - Install ClamAV: `sudo yum install -y clamav clamav-update`
   - Update defs: `sudo freshclam`
   - Package `/usr/bin/clamscan`, `/usr/bin/freshclam`, and `/var/lib/clamav/*` into `clamav-layer.zip`.
   - Upload as a Lambda Layer named `ClamAVLayer`.
3. **Deploy Lambda**:
   - Use `lambda_function.py`.
   - Attach `ClamAVLayer` under Layers.
   - Set S3 trigger on `source-bucket` (Event: `s3:ObjectCreated:*`).
   - Timeout: 5-15 min, Memory: 1024 MB.
4. **Test**:
   - Upload a safe file (e.g., `test.txt`) and an EICAR test file (`https://www.eicar.org/download/eicar-com/`).
   - Verify files move to `production-bucket` (clean) or `quarantine-bucket` (infected).

## Dependencies
- `boto3` (AWS SDK for Python)

## Notes
- Update bucket names in `lambda_function.py`.
- Ensure Lambda IAM role has S3 read/write permissions.
- Rebuild `clamav-layer.zip` periodically to update virus definitions.