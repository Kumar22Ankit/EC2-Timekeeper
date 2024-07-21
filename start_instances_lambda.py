import boto3
import os
import json
from datetime import datetime

# AWS credentials and region
AWS_REGION = 'your_aws_region'
AWS_ACCESS_KEY_ID = 'your_access_key_id'
AWS_SECRET_ACCESS_KEY = 'your_secret_access_key'

# Function to start EC2 instances
def start_instances(event, context):
    # Initialize AWS clients
    ec2_client = boto3.client('ec2', region_name=AWS_REGION,
                              aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    # Get current time
    current_time = datetime.now().time().strftime('%H:%M')

    # Load configuration from config.json (assuming it exists in the same directory)
    with open('config.json') as config_file:
        config = json.load(config_file)
    
    # Check if current time is within company working hours
    company_start_time = datetime.strptime(config['company_hours']['start'], '%H:%M').time()
    company_end_time = datetime.strptime(config['company_hours']['end'], '%H:%M').time()

    if company_start_time <= current_time < company_end_time:
        # Get instances to start based on specified tags
        filters = [
            {'Name': 'tag:environment', 'Values': [config['instance_tags']['environment']]},
            {'Name': 'tag:department', 'Values': [config['instance_tags']['department']]}
        ]
        instances_to_start = ec2_client.describe_instances(Filters=filters)

        # Start each instance
        for reservation in instances_to_start['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                ec2_client.start_instances(InstanceIds=[instance_id])
                print(f'Starting instance: {instance_id}')

        return {
            'statusCode': 200,
            'body': json.dumps('Started instances successfully')
        }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Outside of company working hours, no instances started')
        }
