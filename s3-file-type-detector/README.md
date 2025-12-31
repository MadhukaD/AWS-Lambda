# S3 File Type Detector Lambda

S3 File Type Detector Lambda is a compact AWS Lambda function that triggers on S3 object creation events, reads the uploaded object's metadata to determine its MIME `Content-Type`, and logs the detected file type to CloudWatch.

The function is designed for easy integration into existing S3 event-driven pipelines for validation, routing, auditing, or lightweight metadata enrichment.

## Architecture
- **S3 Bucket**: Receives file uploads
- **Lambda Function**: Extracts bucket/key from event, calls `s3.get_object()`, prints Content-Type
- **IAM Role**: Custom S3 read policy
- **Trigger**: S3 "All object create events"

## Deployment Steps
1. Create S3 bucket: Using AWS Management Console, create a S3 bucket called `file-type-detector`
2. Create Lambda function:
   - Option: Author from scratch
   - Name: `file-type-detector`
   - Runtime: Python 3.14 or an available version
   - Execution Role: Create a new role from AWS policy templates
   - Role name: file-type-detector-s3-role
   - Policy template: `Amazon S3 object read-only permissions`
   <img width="1651" height="604" alt="Screenshot 2025-12-31 094414" src="https://github.com/user-attachments/assets/ccfc32ca-335b-4e64-be8e-92d988f469e5" />
   <img width="1617" height="574" alt="Screenshot 2025-12-31 094440" src="https://github.com/user-attachments/assets/8b86ccf3-8861-4ca6-819f-cb4001e82222" />

4. Configure Lambda function:
   - Go to your function, scroll down to the **Code** tab and add below code to `lambda_function.py` and deploy
   <img width="1654" height="682" alt="image" src="https://github.com/user-attachments/assets/4caaa7d9-31bd-4c91-91d9-2fa21b756bfd" />

   - Go to Function overview (Scroll to top) and add a trigger
     - Source: S3
     - Bucket: `file-type-detector`
     - Event types: All objects create events
     - Acknowledge the recursive invocation
   <img width="1654" height="732" alt="Screenshot 2025-12-31 102524" src="https://github.com/user-attachments/assets/bc5a32ee-545f-4761-ac36-759a1f596a26" />

5. Upload any file to the S3 bucket
6. View the output
     - Go to your function and select Monitor tab
     - Click on the Cloudwatch Logs and select the latest log group
     - Locate the file type output
   <img width="1627" height="429" alt="Screenshot 2025-12-31 103144" src="https://github.com/user-attachments/assets/6ec0c046-eb5b-46b7-bd78-8597a605c1e3" />

## Code (lambda_function.py)
```python
import json          # For event debugging (uncomment print statement)
import urllib.parse  # Decodes URL-encoded object keys (e.g., %20 → space)
import boto3         # AWS SDK for S3 operations

print('Loading function')  # Logs once per cold start

s3 = boto3.client('s3')    # Global client reuses across invocations (best practice)

def lambda_handler(event, context):
    # Parse bucket and object key from S3 event structure
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)  # Head-like operation
        print("CONTENT TYPE: " + response['ContentType']) # Logs to CloudWatch
        return response['ContentType']                    # Optional response
    except Exception as e:
        print(e) # Error details
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e # Re-raises to mark invocation as failed
```
