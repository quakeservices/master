import os
import boto3

from aws_cdk import (
        core,
        aws_certificatemanager as certificatemanager,
        aws_apigateway as apigateway,
        aws_lambda as _lambda,
        aws_s3 as s3,
        aws_iam as iam
)


class WebBackendDeployStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
     
        """
        Get existing certificate
        """
        arn = "arn:aws:acm:{region}:{account}:certificate/{cert}".format(region='us-west-2',
                                                                          account=os.getenv("CDK_DEFAULT_ACCOUNT"),
                                                                          cert='8cf6dd16-eb52-4a8d-b973-e6b0c07e00f5')
        certificate = certificatemanager.Certificate.from_certificate_arn(self,
                                                                          "wildcard_cert",
                                                                          arn)


        policy = iam.PolicyStatement(
            resources=["*"],
            actions=["dynamodb:Get*",
                     "dynamodb:Query",
                     "dynamodb:Scan",
                     "dynamodb:Describe*",
                     "dynamodb:List*"])


        """
        Define domain name and certificate to use for API Gateway
        domain = apigateway.DomainNameOptions(certificate,
                                              domain_name='api.quake.services')
                                            
        """

        """
        Get latest version of code
        There is probably a more elegant way of doing this
        But for now this works
        """
        s3_bucket_name = 'web-backend-lambda-package'
        s3client = boto3.client('s3')
        latest_version = s3client.get_object_tagging(Bucket=s3_bucket_name,
                                                     Key='function.zip')
        bucket = s3.Bucket.from_bucket_name(self,
                                            'bucket',
                                            bucket_name=s3_bucket_name)

        """
        Define Lambda function
        """
        code = _lambda.Code.from_bucket(bucket=bucket,
                                        key='function.zip',
                                        object_version=latest_version.get('VersionId'))

        backend = _lambda.Function(
            self, 'web-backend',
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler='lambda.lambda_handler',
            code=code,
        )

        backend.add_to_role_policy(statement=policy)

        """
        Define API Gateway
        """
        api = apigateway.LambdaRestApi(self,
                                       "QuakeServicesAPI",
                                     # domain_name=[domain],
                                       handler=backend)
