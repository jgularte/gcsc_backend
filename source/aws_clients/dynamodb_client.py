# standard imports
import logging
import json
import six
import uuid
from decimal import Decimal

# external installed imports
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer


class DynamoDBClient:
    """
    class for interfacing with AWS dynamodb
    """

    def __init__(self, config):
        """

        :param config:
        """
        # objects
        self._config = config
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

        # set up main client
        if "endpoint_url" in self._config.keys():
            self._logger.info("Local Dynamo Table")
            self._client = boto3.client("dynamodb", endpoint_url=self._config["endpoint_url"])
        else:
            self._client = boto3.client('dynamodb')

        # table key condition expressions
        self.only_part_key = "#p = :partitionkeyval"

    def write(self, item):
        """
        write a json item to the dynamo table associated with class object
        :param item: dict
        :return: None
        """
        result_ = TypeSerializer().serialize(item)
        dynamo_item = next(six.iteritems(result_))[1]
        try:
            self._client.put_item(
                TableName=self._config['table_name'],
                Item=dynamo_item,
                ReturnValues='NONE'
            )
            self._logger.debug(
                {'write_dynamo_success': f"Lambda dynamo write to ' + {self._config['table_name']}"}
            )
            return None
        except ClientError as e:
            err_message = {'error': 'Lambda dynamo write error', 'msg': str(e)}
            self._logger.error(err_message)
            raise Exception(err_message)

    def scan(self, table_name):
        """

        :param table_name: table to scan
        :return: items
        """
        try:
            result = self._client.scan(
                TableName=table_name
            )
            return result
        except ClientError as e:
            self._logger.error(e)
            raise Exception(e)

    def get_last_invoker(self, partition_value, epoch_end, as_dict=True, replace_decimals=True):
        """
        Use to get the most recent run from a 'run-cache' type table.
        :param partition_value: STRING hash-key to query on
        :param epoch_end: INT sort key to query on
        :param as_dict: BOOL True will return a python dict, False will return the dynamo-type object
        :param replace_decimals: BOOL true will replace Decimals with ints, False wont'
        :return: dict
        """
        if not partition_value:
            raise Exception('No partition value given.')

        try:
            response = self._client.query(
                TableName=self._config['table_name'],
                KeyConditionExpression="#p = :partitionkeyval AND #s < :sortkeyval",
                ExpressionAttributeNames={
                    "#p": self._config['part_key'],
                    "#s": self._config['sort_key']
                },
                Limit=1,
                ConsistentRead=True,
                ScanIndexForward=False,
                ExpressionAttributeValues={
                    ":partitionkeyval": {
                        "S": partition_value
                    },
                    ":sortkeyval": {
                        "N": str(epoch_end)
                    }
                }
            )
            self._logger.debug(
                {'read_dynamo_success': f"Lambda dynamo read to {self._config['table_name']}"}
            )
            if as_dict and len(response["Items"]):
                deserializer = TypeDeserializer()
                for item in response["Items"]:
                    for key in item.keys():
                        item[key] = deserializer.deserialize(item[key])

            if replace_decimals and len(response["Items"]):
                response["Items"] = self.replace_decimals(response["Items"])

            return response["Items"]
        except ClientError as e:
            err_message = {'error': 'Lambda dynamo read error', 'msg': str(e)}
            self._logger.error(err_message)
            raise Exception(err_message)

    def query_inbetween(self, part_val, high, low, as_dict=False):
        """
        Use to query inbetween two sort key values.
        :param part_val: STRING hash-key to partition on
        :param high: INT upper bound of sort key
        :param low:  INT lower bound of sort key
        :param as_dict: BOOL True will return a python dict, False will return the dynamo-type object
        :return: dict
        """
        between_sort_key = "#p = :partitionkeyval AND #s BETWEEN :low AND :high"
        expression_names = {
            "#p": self._config["part_key"],
            "#s": self._config["sort_key"]
        }
        expression_attributes = {
            ":partitionkeyval": {
                self._config["part_key_type"]: part_val
            },
            ":low": {
                self._config["sort_key_type"]: str(low)
            },
            ":high": {
                self._config["sort_key_type"]: str(high)
            }
        }
        return self.query(between_sort_key, expression_names, expression_attributes, as_dict)

    def query(self, key_condition_exp=None, expression_names=None, expression_attribute_vals=None, as_dict=False):
        """
        Use to make a query from scratch, class won't create any of the query params, or attirbute dicts.
        :param key_condition_exp: STRING
        :param expression_names: DICT
        :param expression_attribute_vals: DICT
        :param as_dict: BOOL True will return a python dict, False will return the dynamo-type object
        :return: dict
        """
        try:
            response = self._client.query(
                TableName=self._config['table_name'],
                KeyConditionExpression=key_condition_exp,
                ExpressionAttributeNames=expression_names,
                ExpressionAttributeValues=expression_attribute_vals
            )
            self._logger.debug(
                {'read_dynamo_success': f"Lambda dynamo read to {self._config['table_name']}"}
            )
            if as_dict and len(response["Items"]):
                deserializer = TypeDeserializer()
                for item in response["Items"]:
                    for key in item.keys():
                        item[key] = deserializer.deserialize(item[key])
                return response["Items"]
            else:
                return response["Items"]
        except ClientError as e:
            err_message = {'error': 'Lambda dynamo read error', 'msg': str(e)}
            self._logger.error(err_message)
            raise Exception(err_message)

    def replace_decimals(self, obj):
        """
        helper funciton used to replace Decimal objects with ints if desired
        :param obj: DICT object to convert
        :return: DICT
        """
        if isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = self.replace_decimals(obj[i])
            return obj
        elif isinstance(obj, dict):
            for k, v in obj.items():
                obj[k] = self.replace_decimals(v)
            return obj
        elif isinstance(obj, set):
            return set(self.replace_decimals(i) for i in obj)
        elif isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        else:
            return obj