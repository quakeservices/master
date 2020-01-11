import os
from aws_cdk import (
        core,
        aws_certificatemanager as certificatemanager,
        aws_apigateway as apigateway,
        aws_lambda as _lambda,
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


        """
        Define domain name and certificate to use for API Gateway
        domain = apigateway.DomainNameOptions(certificate,
                                              domain_name='api.quake.services')
                                            
        """

        """
        Define Lambda function
        """
        backend = _lambda.Function(
            self, 'web-backend',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset('web-backend'),
            handler='lambda.lambda_handler',
        )

        """
        Define API Gateway
        """
        api = apigateway.LambdaRestApi(self,
                                       "QuakeServicesAPI",
                                     # domain_name=[domain],
                                       handler=backend)
