from __future__ import annotations

import json
import logging
import uuid
import boto3
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb_client: DynamoDBClient = boto3.client("dynamodb")


def handler(event, context):
    table = os.environ["TABLE_NAME"]
    logging.info(f"## Loaded table name from environment variable DDB_TABLE: {table}")

    if event.get("body"):
        item = json.loads(event["body"])
        logging.info(f"## Received payload: {item}")

        year = str(item["year"])
        title = str(item["title"])
        id = str(item["id"])

        dynamodb_client.put_item(TableName=table, Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}})
        message = "Successfully inserted data!"

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
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
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Successfully inserted default data!"}),
        }
