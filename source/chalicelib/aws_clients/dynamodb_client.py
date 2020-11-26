"""
filename: dynamodb_client.py
author: Jack Gularte
date: Sept. 16 2020

Boto3 Documentation:
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table
All functions use the resource.Table entity to make the calls to DynamoDB and all functions will return the
full response object from Dynamo.
"""

import logging
import json
from boto3.dynamodb import conditions
from typing import Any, Dict, List

# external installed imports
import boto3
from botocore.exceptions import ClientError

# init logger and resource
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
dynamodb = boto3.resource("dynamodb", region_name="us-west-2")


def write(table_name: str, item: Dict = None, return_values="NONE") -> Dict:
    """
    Description: If you are creating an object for the first time, DO NOT use "ALL_OLD" for the return_values.
    It will throw error only use when updating a current item.
    Link: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.put_item

    :param table_name: table to insert into
    :param item: item to insert
    :param return_values: put_item only accepts one of: "NONE", "ALL_OLD"
    :return: None or item, depending on return_values value
    """
    table = dynamodb.Table(table_name)
    try:
        response = table.put_item(
            TableName=table_name,
            Item=item,
            ReturnValues=return_values,
        )
        logger.debug(
            {
                "dynamodb_client": "write",
                "success": True,
                "table_name": table_name,
                "item": json.dumps(item)
            }
        )
        return response

    except ClientError as e:
        logger.error(
            {
                "dynamodb_client": "write",
                "success": False,
                "table_name": table_name,
                "msg": str(e.args[0])
            }
        )
        raise ValueError(
            {
                "dynamodb_client": "write",
                "success": False,
                "table_name": table_name,
                "msg": str(e.args[0])
            }
        )


def batch_write(table_name: str, list_of_items: List[Dict]) -> None:
    """
    Description: batch write put item
    BatchWriter: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.batch_writer
    PutItem: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.put_item

    :param table_name: table to insert into
    :param list_of_items: list of items to insert
    """

    table = dynamodb.Table(table_name)
    with table.batch_writer() as batch:
        for item in list_of_items:
            batch.put_item(Item=item)


def write_conditional(table_name: str, item: Dict, condition_expr: str, return_values="NONE") -> Dict:
    """
    Description: If you are creating a new object, DO NOT have return_values set to ALL_OLD, it will throw an error
    as there is no old object
    Link: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.put_item

    :param table_name: table to insert into
    :param item: dict of item to insert
    :param condition_expr: the condition expression to apply to the write
    :param return_values: whether to return None, or the old values replaced. NONE or ALL_OLD
    :return: dict
    """
    table = dynamodb.Table(table_name)
    try:
        response = table.put_item(
            TableName=table_name,
            Item=item,
            ReturnValues=return_values,
            ConditionExpression=condition_expr
        )
        logger.debug(
            {
                "dynamodb_client": "write",
                "success": True,
                "table_name": table_name,
                "item": json.dumps(item)
            }
        )
        return response
    except ClientError as e:
        logger.error(
            {
                "dynamodb_client": "write_conditional",
                "success": False,
                "table_name": table_name,
                "msg": str(e.args[0])
            }
        )
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise ValueError("ConditionalCheckFailed")
        else:
            raise ValueError(
                {
                    "dynamodb_client": "write",
                    "success": False, "tablename": table_name,
                    "msg": str(e.args[0])
                }
            )


def update_item(table_name: str, key: dict, updates: Dict, return_values="NONE") -> Dict:
    """
    Link: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.update_item

    :param table_name: table to insert into
    :param update: dict of {<field_name>:{'Value':<value>, 'Action':ADD, DELETE or PUT}}
    :param return_values: put_item only accepts one of: "NONE", "ALL_OLD"
    :return: None or item, depending on return_values value
    """
    table = dynamodb.Table(table_name)
    try:

        response = table.update_item(
            Key=key,
            AttributeUpdates=updates,
            ReturnValues=return_values,
        )
        logger.debug(
            {
                "dynamodb_client": "update",
                "success": True,
                "table_name": table_name
            }
        )
        return response

    except ClientError as e:
        logger.error(
            {
                "dynamodb_client": "write",
                "success": False,
                "table_name": table_name,
                "msg": str(e.args[0])
            }
        )
        raise ValueError(
            {
                "dynamodb_client": "write",
                "success": False,
                "table_name": table_name,
                "msg": str(e.args[0])
            }
        )


def scan_table(table_name: str) -> Dict:
    """
    Description: Scan the given table
    Link: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.scan

    :param table_name: table to scan
    :return: dict
    """
    try:
        table = dynamodb.Table(table_name)

        # set operation flags and init results
        done = False
        start_key = None
        scan_kwargs = {}
        result = []
        response = {}
        # loop and use the last evaluated key as a starting point for each page
        while not done:
            if start_key:
                scan_kwargs["ExclusiveStartKey"] = start_key
            response = table.scan(**scan_kwargs)
            start_key = response.get("LastEvaluatedKey", None)
            result = response.get("Items", [])
            done = start_key is None

        # append the full items list to the last response object
        response["Items"] = result
        return response
    except ClientError as e:
        raise e


def get_item(table_name: str, key: Dict) -> Dict:
    """
    Description: Get a single item from the table
    Link: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.get_item

    :param table_name: table to get item from
    :param key: item key to search for -> {'<primary_key_name>':'<primary_key_value>'}
     or {'<primary_key_name>':'<primary_key_value>', '<sort_key_name>':'<sort_key_value>'}
    :return: dict
    """
    try:
        table = dynamodb.Table(table_name)
        logger.debug(
            {
                "dynamodb_client": "get_item",
                "success": True,
                "table_name": table_name
            }
        )
        return table.get_item(Key=key)
    except ClientError as e:
        err_message = {
            'dynamodb_client': 'get_item',
            'success': False,
            'msg': str(e.args[0]),
        }

        logger.error(err_message)
        raise Exception(err_message)


def get_item_count(table_name: str, primary_key: str, primary_key_val: str, query_index=False) -> int:
    """
    Description: Use to make a query with primary key equal to value and get count back of occurrences
    Link: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.query

    :param table_name: table to search through
    :param primary_key: the primary key of the table
    :param primary_key_val: the value of the primary key to search for
    :return: dict
    """

    table = dynamodb.Table(table_name)
    if not query_index:
        response = table.query(
            TableName=table_name,
            KeyConditionExpression=conditions.Key(primary_key).eq(primary_key_val),
            Select="COUNT"
        )["Count"]
    else:
        response = table.query(
            IndexName=table_name,
            KeyConditionExpression=conditions.Key(primary_key).eq(primary_key_val),
            Select="COUNT"
        )["Count"]
    logger.debug(
        {
            "dynamodb_client": "query_matchPrimary_search_betweenSort",
            "success": True,
            "table_name": table_name,
        }
    )
    return response


def delete_item(table_name: str, item: Dict, return_values="NONE") -> Dict:
    """
    Description: delete an item based on the item keys passed into function
    Link: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.delete

    :param table_name: table to delete from
    :param item: item to check for
    :param return_values: what values to return, reference boto3 documentation
    :return: dict
    """
    try:
        table = dynamodb.Table(table_name)
        return table.delete_item(
            Key=item,
            ReturnValues=return_values
        )
    except ClientError as e:
        raise e


def match_primary(table_name: str, primary_key: str, primary_key_val: str or int, index_name: str = None,
                       query_index=False) -> Dict:
    """
    Description: Use to make a query with primary key equal to value
    Link: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.query

    :param table_name: table to search through
    :param primary_key: the primary key of the table
    :param primary_key_val: the value of the primary key to search for
    :return: dict
    """

    table = dynamodb.Table(table_name)
    if not query_index:
        response = table.query(
            TableName=table_name,
            KeyConditionExpression=conditions.Key(primary_key).eq(primary_key_val)
        )
    else:
        response = table.query(
            IndexName=index_name,
            KeyConditionExpression=conditions.Key(primary_key).eq(primary_key_val)
        )
    logger.debug(
        {
            "dynamodb_client": "query_matchPrimary_search_betweenSort",
            "success": True,
            "table_name": table_name,
        }
    )
    return response


def query_keyCondition_filterExp(table_name: str, key_conditions, filter_expressions, index_name: str = None) -> Dict:
    """
    Description: Use to make a query with primary key equal to value
    Link: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.query

    :param table_name: table to search through
    :param key_conditions: key condition expressions -> use make_key_conditions
    :param filter_expressions: filter expressions -> use make filter_conditions
    :param index_name: Required only if searching an index.
    :return: dict
    """

    table = dynamodb.Table(table_name)
    if index_name is None:
        return table.query(
            TableName=table_name,
            KeyConditionExpression=key_conditions,
            FilterExpression=filter_expressions
        )
    else:
        return table.query(
            IndexName=index_name,
            KeyConditionExpression=key_conditions,
            FilterExpression=filter_expressions
        )


def match_primary_between_sort(
        table_name,
        primary_key,
        primary_key_val,
        sort_key,
        sort_key_val_low,
        sort_key_val_high) -> Dict:
    """
    Description: Use to make a query with primary key equal to value and sort key in between specific values
    Link: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.query

    :param table_name: table to search through
    :param primary_key: the primary key of the table
    :param primary_key_val: the value of the primary key to search for
    :param sort_key: the sort key of the table
    :param sort_key_val_low: the low end of the search range
    :param sort_key_val_high: the high end of the search range
    :return: dict
    """
    try:
        table = dynamodb.Table(table_name)
        response = table.query(
            TableName=table_name,
            KeyConditionExpression=conditions.Key(primary_key).eq(primary_key_val)
                                   & conditions.Key(sort_key).between(sort_key_val_low, sort_key_val_high),
        )
        logger.debug(
            {
                "dynamodb_client": "query_matchPrimary_search_betweenSort",
                "success": True,
                "table_name": table_name,
            }
        )
        return response
    except ClientError as e:
        err_message = {
            "dynamodb_client": "query_matchPrimary_search_betweenSort",
            "success": False,
            "msg": str(e.args[0]),
        }
        logger.error(err_message)
        raise Exception(err_message)


def query(table_name: str, query_params: Dict) -> Dict:
    """
    Description: Use to make a query from scratch, does not create any of the query params, or attribute dicts.
    Link: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.query

    :param table_name: table to query
    :param query_params: dict, query_params
    :return: dict
    """
    try:
        # table.query(**kwargs) does not handle None types
        # the client is required to make a parameters dict according to the docs
        table = dynamodb.Table(table_name)
        response = table.query(**query_params)
        logger.debug(
            {
                "dynamodb_client": "query",
                "success": True,
                "table_name": table_name
            }
        )
        return response
    except ClientError as e:
        err_message = {
            "dynamodb_client": "query",
            "success": False,
            "msg": str(e.args[0]),
        }
        logger.error(err_message)
        raise Exception(err_message)
    except Exception as e:
        err_message = {
            "dynamodb_client": "query",
            "success": False,
            "msg": e
        }
        logger.error(err_message)
        raise Exception(err_message)


def make_filter_expressions(list_of_filter_dicts: list):
    """
    Attr: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/dynamodb.html#boto3.dynamodb.conditions.Attr

    Create a filter expressions concatenated string to be used in dynamodb query.
    ['begins_with', 'between', 'eq', 'gt', 'gte', 'lt', 'lte', 'attribute_type', 'contains',
     'exists', 'is_in', 'ne', 'not_exists', 'size']
    :param list_of_filter_dicts: List of filter expressions (Attr link) -> example_entry: {'key':<key>, 'value': <value>, 'operator': <operator>}.
    If value requires range, use a tuple for values (<HIGH_VALUE>, <LOW_VALUE>)
    :return: String of filter expressions
    """
    filter_expressions: Any = None
    first = True
    for filter_dict in list_of_filter_dicts:
        # concatenate filters
        if first:
            filter_expressions = _add_condition(conditions.Attr(filter_dict['key']), filter_dict['operator'],
                                                filter_dict['value'])
            first = False
        else:
            filter_expressions = filter_expressions & _add_condition(conditions.Attr(filter_dict['key']),
                                                                     filter_dict['operator'], filter_dict['value'])
    return filter_expressions


def make_key_conditions(list_of_keys_dicts):
    """
    Key: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/dynamodb.html#boto3.dynamodb.conditions.Key

    Create a ke expressions concatenated string to be used in dynamodb query.

    :param list_of_keys_dicts: List of MAX TWO dicts, first entry is primary key, second is sort key (key link) ->
    example_entry: {'key':<key>, 'value':<value>, 'operator':<operator>}
    If value requires range, use a tuple for values (<HIGH_VALUE>, <LOW_VALUE>)
    :return: concatenated key condition
    """
    key_conditions: Any = None
    first = True
    for key_dict in list_of_keys_dicts:
        if first:
            key_conditions = _add_condition(conditions.Key(key_dict['key']), key_dict['operator'], key_dict['value'])
            first = False
        else:
            key_conditions = key_conditions & _add_condition(conditions.Key(key_dict['key']), key_dict['operator'],
                                                             key_dict['value'])
    return key_conditions


def _add_condition(item: Any or conditions.Key or conditions.Attr, operator: str, value: Any):
    # for operators that requires range, extract tuple
    if isinstance(value, tuple):
        value_high = value[0]
        value_low = value[1]
    if operator == 'eq':
        return item.eq(value)
    if operator == "ne":
        return item.ne(value)
    if operator == 'not_exists':
        return item.not_exists()
    # TODO: implement rest of operators
    return item
