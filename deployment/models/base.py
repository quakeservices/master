from pydantic import BaseModel, ConfigDict


class DeploymentBaseModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, strict=True, frozen=True)
