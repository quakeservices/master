from typing import Any

from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_route53 as route53
from constructs import Construct

DEFAULT_TTL: Duration = Duration.minutes(30)
DEFAULT_DELETE_EXISTING: bool = True
DEFAULT_REMOVAL_POLICY: RemovalPolicy = RemovalPolicy.DESTROY


class Record(route53.RecordSet):
    def __init__(
        self,
        scope: Construct,
        zone: route53.IHostedZone | None,
        domain: str,
        record_type: route53.RecordType,
        record_name: str,
        record_target: route53.RecordTarget,
        ttl: Duration = DEFAULT_TTL,
        delete_existing: bool = DEFAULT_DELETE_EXISTING,
        removal_policy: RemovalPolicy = DEFAULT_REMOVAL_POLICY,
    ):
        if zone is None:
            zone = self._lookup(domain)

        super().__init__(
            scope,
            f"{domain}-{record_name}-{record_type}".lower(),
            record_type=record_type,
            target=record_target,
            zone=zone,
            delete_existing=delete_existing,
            record_name=record_name,
            ttl=ttl,
        )
        self.apply_removal_policy(removal_policy)

    def _lookup(self, domain: str) -> route53.IHostedZone:
        return route53.HostedZone.from_lookup(
            self, f"domain-{domain}", domain_name=domain
        )


class RecordBuilder(Construct):
    record_types: list[str] = [record_type.name for record_type in route53.RecordType]
    zones: dict[str, route53.IHostedZone]

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        zones: dict[str, route53.IHostedZone],
    ):
        super().__init__(scope, construct_id)
        self.zones = zones

    def create_record(
        self,
        domain: str,
        record_type: str | route53.RecordType | None,
        record_name: str,
        record_target: list[str] | route53.RecordTarget | None,
        ttl: Duration = DEFAULT_TTL,
        delete_existing: bool = DEFAULT_DELETE_EXISTING,
        removal_policy: RemovalPolicy = DEFAULT_REMOVAL_POLICY,
    ) -> Record | None:
        zone: route53.IHostedZone | None = self.zones.get(domain)
        record_type = self._type_to_object(record_type)
        record_target = self._target_to_object(record_target)

        if self._validate(zone, record_type, record_target) is False:
            return None

        return Record(
            self,
            zone,
            domain,
            record_type,
            record_name,
            record_target,
            ttl,
            delete_existing,
            removal_policy,
        )

    @staticmethod
    def _validate(
        zone: route53.IHostedZone | None,
        record_type: str | route53.RecordType | None,
        record_target: list[str] | route53.RecordTarget | None,
    ) -> bool:
        errors: list[str] = []
        if zone is None:
            errors.append("Zone not found")
        if record_type is None:
            errors.append("Record type not found")
        if record_target is None:
            errors.append("Record target not found")

        if errors:
            print("\n".join(errors))
            return False

        return True

    @classmethod
    def _type_to_object(
        cls,
        record_type: str | route53.RecordType,
    ) -> route53.RecordType | None:
        result: route53.RecordType | None = None

        if isinstance(record_type, str) and hasattr(
            route53.RecordType, record_type.upper()
        ):
            result = getattr(route53.RecordType, record_type.upper())

        if isinstance(record_type, route53.RecordType):
            result = record_type

        return result

    @classmethod
    def _target_to_object(
        cls,
        record_target: list[str] | route53.RecordTarget,
    ) -> route53.RecordTarget | None:
        result: route53.RecordTarget | None = None

        if cls._is_list_of_strings(record_target):
            result = route53.RecordTarget(values=record_target)  # type: ignore

        if isinstance(record_target, route53.RecordTarget):
            result = record_target

        return result

    @staticmethod
    def _is_list(value: Any) -> bool:
        return isinstance(value, list)

    @classmethod
    def _is_list_of_strings(cls, value: Any) -> bool:
        return cls._is_list(value) and all(isinstance(entity, str) for entity in value)
