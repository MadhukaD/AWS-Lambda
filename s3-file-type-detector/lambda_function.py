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