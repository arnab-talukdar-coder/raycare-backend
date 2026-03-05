import uuid
from typing import Any, Optional

import boto3
from boto3.dynamodb.conditions import Attr, Key

from src.common.config import settings


_dynamodb = boto3.resource("dynamodb", region_name=settings.region)


class DynamoRepository:
    def __init__(self, table_name: str):
        self.table = _dynamodb.Table(table_name)

    def put(self, item: dict[str, Any]) -> dict[str, Any]:
        self.table.put_item(Item=item)
        return item

    def get(self, pk_name: str, pk_value: str, sk_name: Optional[str] = None, sk_value: Optional[str] = None):
        key = {pk_name: pk_value}
        if sk_name and sk_value:
            key[sk_name] = sk_value
        response = self.table.get_item(Key=key)
        return response.get("Item")

    def query_pk(self, pk_name: str, pk_value: str, index_name: Optional[str] = None):
        kwargs = {"KeyConditionExpression": Key(pk_name).eq(pk_value)}
        if index_name:
            kwargs["IndexName"] = index_name
        response = self.table.query(**kwargs)
        return response.get("Items", [])

    def scan(self, filter_expression=None):
        kwargs = {}
        if filter_expression is not None:
            kwargs["FilterExpression"] = filter_expression
        response = self.table.scan(**kwargs)
        return response.get("Items", [])

    def update(self, key: dict, update_expression: str, names: dict, values: dict):
        response = self.table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
            ReturnValues="ALL_NEW",
        )
        return response["Attributes"]


def new_uuid() -> str:
    return str(uuid.uuid4())


def attr_equals(name: str, value: Any):
    return Attr(name).eq(value)
