from pydantic import BaseModel,Field

class NetworkDevice(BaseModel):
    device_type: str 
    host: str =  Field(None, description="Who sends the error message.")
    username: str
    password: str


class NetworkDeviceUpdate(BaseModel):
    device_type: str = Field(None)
    host: str = Field(None)
    username: str = Field(None)
    password: str = Field(None)
    use_payload: bool = Field(default=False)