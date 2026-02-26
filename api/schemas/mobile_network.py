from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union

class LocationData(BaseModel):
    latitude: float = Field(..., alias="Latitude")
    longitude: float = Field(..., alias="Longitude")
    altitude: float = Field(..., alias="Altitude")
    time: int = Field(..., alias="Time")

class MobileNetworkData(BaseModel):
    networkType: str = Field(..., alias="NetworkType")
    cellIdentity: str = Field(..., alias="CellIdentity")
    mcc: Optional[str] = Field(None, alias="MCC")
    mnc: Optional[str] = Field(None, alias="MNC")
    pci: int = Field(..., alias="PCI")
    tac: int = Field(..., alias="TAC")
    bands: str = Field(..., alias="Bands")
    signalStrength: str = Field(..., alias="SignalStrength")
    rsrp: int = Field(..., alias="RSRP")
    rsrq: int = Field(..., alias="RSRQ")
    rssi: int = Field(..., alias="RSSI")
    timingAdvance: int = Field(..., alias="TimingAdvance")
    time: int = Field(..., alias="Time")

class MobileNetworkDataList(BaseModel):
    mobileNetworks: List[MobileNetworkData] = Field(..., alias="MobileNetworks")

class MobileDataSaveRequest(BaseModel):
    mobile_network_data_list: Optional[Union[MobileNetworkDataList, List[MobileNetworkData]]] = None
    location_data: Optional[LocationData] = None

class MobileDataResponseItem(BaseModel):
    user_id: Optional[str] = None
    nickname: Optional[str] = None
    data: Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]
    page: int
    count: int

class UserWithNickname(BaseModel):
    user_id: str
    nickname: Optional[str] = None

class UsersWithDataResponse(BaseModel):
    users: List[UserWithNickname]
    total: int

class SuccessResponse(BaseModel):
    message: str