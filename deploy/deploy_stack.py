import os
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
        Define Lambda function
        """
        bucket = s3.Bucket.from_bucket_name(self,
                                            'bucket',
                                            bucket_name='web-backend-lambda-package')

        code = _lambda.Code.from_bucket(bucket=bucket,
                                        key='function.zip',
                                        object_version='vCsm2bZfXZN0..Cg7vy00HAvWT_jnLmJ')

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
