"""
Pydantic schemas for the IoT EV Fleet Management backend.

These schemas define the shapes for create/update/read operations of the key entities.
They are designed to avoid exposing sensitive information (e.g., password_hash is excluded from reads).
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


# Shared mixins
class ORMModel(BaseModel):
    """Base Pydantic model configured for ORM mode."""
    model_config = {"from_attributes": True}


# Role
class RoleBase(ORMModel):
    name: str = Field(..., description="Role name (unique)")
    description: Optional[str] = Field(None, description="Description of the role")


class RoleCreate(RoleBase):
    pass


class RoleRead(RoleBase):
    id: str
    created_at: datetime


# User
class UserBase(ORMModel):
    email: EmailStr = Field(..., description="Unique user email")
    full_name: Optional[str] = Field(None, description="Full name of the user")
    is_active: bool = Field(default=True, description="Active state of the user")


class UserCreate(UserBase):
    password: str = Field(..., description="Plain text password to be hashed server-side")


class UserUpdate(ORMModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, description="New password to be hashed")


class UserRead(UserBase):
    id: str
    roles: List[RoleRead] = []
    created_at: datetime
    updated_at: datetime


# Vehicle
class VehicleBase(ORMModel):
    vin: str = Field(..., description="Unique vehicle VIN")
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    battery_capacity_kwh: Optional[float] = None
    is_active: bool = True


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(ORMModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    battery_capacity_kwh: Optional[float] = None
    is_active: Optional[bool] = None


class VehicleRead(VehicleBase):
    id: str
    created_at: datetime


# Telemetry
class TelemetryBase(ORMModel):
    vehicle_id: str
    timestamp: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    speed_kmh: Optional[float] = None
    battery_soc: Optional[float] = Field(None, description="State of charge percent")
    battery_soh: Optional[float] = Field(None, description="State of health percent")
    temperature_c: Optional[float] = None
    odometer_km: Optional[float] = None
    charging: bool = False
    raw_payload: Optional[str] = None


class TelemetryCreate(TelemetryBase):
    pass


class TelemetryRead(TelemetryBase):
    id: str


# ChargingStation
class ChargingStationBase(ORMModel):
    name: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_power_kw: Optional[float] = None
    is_active: bool = True


class ChargingStationCreate(ChargingStationBase):
    pass


class ChargingStationUpdate(ORMModel):
    name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_power_kw: Optional[float] = None
    is_active: Optional[bool] = None


class ChargingStationRead(ChargingStationBase):
    id: str
    created_at: datetime


# ChargingSession
class ChargingSessionBase(ORMModel):
    vehicle_id: Optional[str] = None
    station_id: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    energy_kwh: Optional[float] = None
    cost: Optional[float] = None


class ChargingSessionCreate(ChargingSessionBase):
    pass


class ChargingSessionRead(ChargingSessionBase):
    id: str


# Alert
class AlertBase(ORMModel):
    vehicle_id: Optional[str] = None
    type: str
    severity: str
    message: Optional[str] = None
    acknowledged: bool = False


class AlertCreate(AlertBase):
    pass


class AlertUpdate(ORMModel):
    acknowledged: Optional[bool] = None


class AlertRead(AlertBase):
    id: str
    created_at: datetime


# Schedule
class ScheduleBase(ORMModel):
    vehicle_id: str
    start_time: datetime
    end_time: datetime
    task: str
    notes: Optional[str] = None


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleRead(ScheduleBase):
    id: str


# Trip
class TripBase(ORMModel):
    vehicle_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    start_latitude: Optional[float] = None
    start_longitude: Optional[float] = None
    end_latitude: Optional[float] = None
    end_longitude: Optional[float] = None
    distance_km: Optional[float] = None
    avg_speed_kmh: Optional[float] = None


class TripCreate(TripBase):
    pass


class TripRead(TripBase):
    id: str
