from aws_cdk import Duration, RemovalPolicy
from pydantic import Field

from deployment.models.base import DeploymentBaseModel


class RecordSetConfiguration(DeploymentBaseModel):
    name: str
    record_type: str = Field(pattern=r"^(A|AAAA|CNAME|MX|NAPTR|NS|PTR|SOA|SRV|TXT)$")
    record_targets: list[str] = Field(default_factory=list)
    ttl: Duration = Duration.minutes(30)
    delete_existing: bool = True
    removal_policy: RemovalPolicy = RemovalPolicy.DESTROY


class RecordsConfiguration(DeploymentBaseModel):
    domain: str
    record_sets: list[RecordSet]
