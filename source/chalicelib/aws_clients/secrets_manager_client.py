"""
filename: secrets_manager_client.py
author: Jack Gularte
date: Nov. 25 2020

This comes from boto3 docs
"""
import boto3
import json
import base64
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_secret(secret_id: str, secret_key: str, region_name="us-west-2") -> str or bytes:
    """
    get a secret key from the secret id
    :param secret_id: the secret id to look in
    :param secret_key: the specific secret key to extract
    :param region_name: the aws region to operate in
    :return: either the secret itself or the binary representation
    """
    # Create a Secrets Manager client
    session = boto3.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_id
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.error("The requested secret " + secret_id + " was not found")
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            logger.error("The request was invalid due to: ", e)
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            logger.error("The request had invalid params: ", e)
        logger.error({"secrets_manager": "get_secret", "success": False, "msg": str(e.args[0])})
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary, only one of these fields will be populated
        logger.debug({"secrets_manager": "get_secret", "success": True})
        if 'SecretString' in get_secret_value_response:
            try:
                return json.loads(get_secret_value_response["SecretString"])[secret_key]
            except KeyError as ke:
                logger.error({"secrets_manager": "get_secret", "success": False, "msg": str(ke.args[0])})
        else:
            return base64.b64decode(get_secret_value_response["SecretBinary"])
