from __future__ import annotations

import json
import logging
import uuid
import boto3
import os
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from aws_lambda_typing.context import Context
    from aws_lambda_typing.events import APIGatewayProxyEventV2
    from mypy_boto3_dynamodb import DynamoDBClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb_client: DynamoDBClient = boto3.client("dynamodb")


def handler(event: APIGatewayProxyEventV2, context: Context) -> dict[str, Any]:
    table = os.environ["TABLE_NAME"]
    logging.info(f"## Loaded table name from environment variable DDB_TABLE: {table}")

    body = event.get("body")
    if body:
        item = json.loads(body)
        logging.info(f"## Received payload: {item}")

        year = str(item["year"])
        title = str(item["title"])
        id = str(item["id"])

        dynamodb_client.put_item(TableName=table, Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}})
        message = "Successfully inserted data!"

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "https://myapp.example.com",
            },
            "body": json.dumps({"message": message}),
        }
    else:
        logging.info("## Received request without a payload")
        dynamodb_client.put_item(
            TableName=table,
            Item={
                "year": {"N": "2012"},
                "title": {"S": "This is empty title"},
                "id": {"S": str(uuid.uuid4())},
            },
        )
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "https://myapp.example.com",
            },
            "body": json.dumps({"message": "Successfully inserted default data!"}),
        }
