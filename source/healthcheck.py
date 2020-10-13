def handler(event, context):
    return {
        "statusCode": 200,
        "body": {
            "message": "I am healthy"
        }
    }