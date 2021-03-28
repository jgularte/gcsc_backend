"""
filename: cognito_client.py
author: Jack Gularte
date: Feb 28 2021
"""

# standard imports
import boto3
import json
import logging
from typing import Dict, List

# chalice imports
from chalice import Response

cognito = boto3.client("cognito-idp")
AUTH_FLOW = "USER_PASSWORD_AUTH"


def admin_create_user(user_pool_id: str, username: str, temp_password: str, attributes: List[Dict]) -> Dict:
    return cognito.admin_create_user(
        UserPoolId=user_pool_id,
        Username=username,
        TemporaryPassword=temp_password,
        UserAttributes=attributes,
        MessageAction="SUPPRESS"
    )


def init_auth_flow(client_id: str, username: str, password_hash: str) -> Dict:
    return cognito.initiate_auth(
        AuthFlow=AUTH_FLOW,
        AuthParameters={
            "USERNAME": username,
            "PASSWORD": password_hash
        },
        ClientId=client_id
    )


def respond_to_auth_challenge(client_id: str, session: str, challenge: str, challenge_params: Dict) -> Dict:
    if challenge == "NEW_PASSWORD_REQUIRED":
        assert "NEW_PASSWORD" in challenge_params

    return cognito.respond_to_auth_challenge(
        ClientId=client_id,
        Session=session,
        ChallengeName=challenge,
        ChallengeResponses=challenge_params
    )


def get_user_via_access_token(access_token: str) -> Dict:
    return cognito.get_user(
        AccessToken=access_token
    )
