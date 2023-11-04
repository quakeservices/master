from aws_cdk import aws_route53 as route53
from aws_cdk import RemovalPolicy, Duration
from constructs import Construct
from typing import Any


class Record(route53.RecordSet):
    def __init__(
        self,
        scope: Construct,
        zone: route53.IHostedZone | None,
        domain: str,
        record_type: route53.RecordType,
        record_name: str,
        record_target: route53.RecordTarget,
        ttl: Duration = Duration.minutes(30),
        delete_existing: bool = True,
        removal_policy: RemovalPolicy = RemovalPolicy.DESTROY,
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
        record_target: list[str] | list[route53.RecordTarget] | None,
    ) -> Record | None:
        zone: route53.IHostedZone | None = self.zones.get(domain)
        record_type = self._type_to_object(record_type)
        record_target = self._target_to_object(record_target)

        if zone is None or record_type is None or record_target is None:
            return None

        return Record(self, zone, domain, record_type, record_name, record_target)

    @classmethod
    def _type_to_object(
        cls,
        record_type: str | route53.RecordType,
    ) -> route53.RecordType | None:
        if (
            cls._is_string(record_type)
            and record_type.upper() in route53.RecordType._member_names_
        ):
            return getattr(route53.RecordType, record_type, None)

        if isinstance(record_type, route53.RecordType):
            return record_type

        return None

    @classmethod
    def _target_to_object(
        cls,
        record_target: list[str] | route53.RecordTarget,
    ) -> route53.RecordTarget | None:
        if cls._is_list_of_strings(record_target):
            return route53.RecordTarget(values=record_target)

        if isinstance(record_target, route53.RecordTarget):
            return record_target

        return None

    @staticmethod
    def _is_string(value: Any) -> bool:
        return isinstance(value, str)

    @staticmethod
    def _is_list(value: Any) -> bool:
        return isinstance(value, list)

    @classmethod
    def _is_list_of_strings(cls, value: Any) -> bool:
        return cls._is_list(value) and all(cls._is_string(entity) for entity in value)
