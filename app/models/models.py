from pydantic import BaseModel, Field


class NetworkDevice(BaseModel):
    device_type: str
    host: str = Field(None)
    username: str
    password: str


class NetworkDeviceUpdate(BaseModel):
    device_type: str = Field(None)
    host: str = Field(None)
    username: str = Field(None)
    password: str = Field(None)
    use_payload: bool = Field(default=False)


class ConfigurationTemplate(BaseModel):
    device_type: str
    filename: str
    description: str = Field(None)
    title: str
