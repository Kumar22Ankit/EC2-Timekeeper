import boto3
import os
import json
from datetime import datetime

# AWS credentials and region
AWS_REGION = 'your_aws_region'
AWS_ACCESS_KEY_ID = 'your_access_key_id'
AWS_SECRET_ACCESS_KEY = 'your_secret_access_key'

# Function to stop EC2 instances
def stop_instances(event, context):
    # Initialize AWS clients
    ec2_client = boto3.client('ec2', region_name=AWS_REGION,
                              aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    # Get current time
    current_time = datetime.now().time().strftime('%H:%M')

    # Load configuration from config.json (assuming it exists in the same directory)
    with open('config.json') as config_file:
        config = json.load(config_file)
    
    # Check if current time is outside company working hours
    company_start_time = datetime.strptime(config['company_hours']['start'], '%H:%M').time()
    company_end_time = datetime.strptime(config['company_hours']['end'], '%H:%M').time()

    if current_time >= company_end_time or current_time < company_start_time:
        # Get instances to stop based on specified tags
        filters = [
            {'Name': 'tag:environment', 'Values': [config['instance_tags']['environment']]},
            {'Name': 'tag:department', 'Values': [config['instance_tags']['department']]}
        ]
        instances_to_stop = ec2_client.describe_instances(Filters=filters)

        # Stop each instance
        for reservation in instances_to_stop['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                ec2_client.stop_instances(InstanceIds=[instance_id])
                print(f'Stopping instance: {instance_id}')

        return {
            'statusCode': 200,
            'body': json.dumps('Stopped instances successfully')
        }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Within company working hours, no instances stopped')
        }
