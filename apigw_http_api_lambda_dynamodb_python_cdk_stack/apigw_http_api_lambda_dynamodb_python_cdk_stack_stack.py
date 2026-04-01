from typing import cast, Sequence
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb_,
    aws_lambda as lambda_,
    aws_apigateway as apigw_,
    aws_ec2 as ec2,
    aws_iam as iam,
    Duration,
)

TABLE_NAME = "demo_table"


class ApigwHttpApiLambdaDynamodbPythonCdkStackStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "ApigwHttpApiLambdaDynamodbPythonCdkStackQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

        vpc = ec2.Vpc(
            self,
            id="Ingress",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Private Subnet", subnet_type=ec2.SubnetType.PRIVATE_ISOLATED, cidr_mask=24
                )
            ],
        )

        dynamo_db_endpoint = ec2.GatewayVpcEndpoint(
            self, id="DynamoDBVpc", service=ec2.GatewayVpcEndpointAwsService.DYNAMODB, vpc=vpc
        )

        dynamo_db_endpoint.add_to_policy(
            iam.PolicyStatement(
                principals=cast(Sequence[iam.IPrincipal], [iam.AnyPrincipal()]),
                actions=[
                    "dynamodb:DescribeStream",
                    "dynamodb:DescribeTable",
                    "dynamodb:Get*",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dynamodb:CreateTable",
                    "dynamodb:Delete*",
                    "dynamodb:Update*",
                    "dynamodb:PutItem",
                ],
                resources=["*"],
            )
        )

        demo_table = dynamodb_.Table(
            self,
            TABLE_NAME,
            partition_key=dynamodb_.Attribute(
                name="id",
                type=dynamodb_.AttributeType.STRING,
            ),
        )

        api_handler = lambda_.Function(
            self,
            "ApiHandler",
            function_name="apigw_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda/apigw-handler"),
            handler="index.handler",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
            ),
            memory_size=1024,
            timeout=Duration.minutes(5),
        )

        demo_table.grant_write_data(api_handler)
        api_handler.add_environment("TABLE_NAME", demo_table.table_name)

        apigw_.LambdaRestApi(
            self,
            "Endpoint",
            handler=cast(lambda_.IFunction, api_handler),
            # default_cors_preflight_options=apigw_.CorsOptions(
            #     allow_origins=["https://myapp.example.com"],  # your allowed origin(s)
            #     allow_methods=apigw_.Cors.ALL_METHODS,
            #     allow_headers=["Content-Type", "Authorization"],
            # ),
        )
