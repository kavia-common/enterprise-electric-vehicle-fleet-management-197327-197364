"""
SQLAlchemy ORM models for the IoT EV Fleet Management backend.

Entities:
- Role, User (with many-to-many relation via user_roles)
- Vehicle
- Telemetry (time-series)
- ChargingStation
- ChargingSession
- Alert
- Schedule
- Trip

Design notes:
- Uses UUID primary keys for most entities for safer cross-system references.
- Timestamps default to timezone-aware now() at DB side when possible.
- Indexes added for frequent query fields (e.g., telemetry timestamps, vehicle references).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Table,
    Column,
    String,
    DateTime,
    Boolean,
    Float,
    ForeignKey,
    Text,
    Integer,
    Index,
    UniqueConstraint,
    func,
)

from sqlalchemy.orm import relationship, Mapped, mapped_column

from .database import Base

# Detect if PostgreSQL dialect UUID is available from DATABASE_URL; if not, fall back to String
# To keep it simple and portable, use String(36) for UUIDs; can be migrated to native UUID per DB later.
UUID_STR = String(36)


def _uuid_str() -> str:
    return str(uuid.uuid4())


# Association table for many-to-many User-Role
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID_STR, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID_STR, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("user_id", "role_id", name="uq_user_role"),
)

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=_uuid_str)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    users: Mapped[list["User"]] = relationship("User", secondary=user_roles, back_populates="roles")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=_uuid_str)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    roles: Mapped[list[Role]] = relationship("Role", secondary=user_roles, back_populates="users")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=_uuid_str)
    vin: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    make: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    year: Mapped[Optional[int]] = mapped_column(Integer)
    battery_capacity_kwh: Mapped[Optional[float]] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    telemetries: Mapped[list["Telemetry"]] = relationship("Telemetry", back_populates="vehicle", cascade="all, delete-orphan")
    charging_sessions: Mapped[list["ChargingSession"]] = relationship("ChargingSession", back_populates="vehicle")
    trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="vehicle")
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="vehicle")
    schedules: Mapped[list["Schedule"]] = relationship("Schedule", back_populates="vehicle")


class Telemetry(Base):
    __tablename__ = "telemetry"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=_uuid_str)
    vehicle_id: Mapped[str] = mapped_column(UUID_STR, ForeignKey("vehicles.id", ondelete="CASCADE"), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    speed_kmh: Mapped[Optional[float]] = mapped_column(Float)
    battery_soc: Mapped[Optional[float]] = mapped_column(Float)  # state of charge %
    battery_soh: Mapped[Optional[float]] = mapped_column(Float)  # state of health %
    temperature_c: Mapped[Optional[float]] = mapped_column(Float)
    odometer_km: Mapped[Optional[float]] = mapped_column(Float)
    charging: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    raw_payload: Mapped[Optional[str]] = mapped_column(Text)

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="telemetries")

    __table_args__ = (
        Index("ix_telemetry_vehicle_time", "vehicle_id", "timestamp"),
    )


class ChargingStation(Base):
    __tablename__ = "charging_stations"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=_uuid_str)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    max_power_kw: Mapped[Optional[float]] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    charging_sessions: Mapped[list["ChargingSession"]] = relationship("ChargingSession", back_populates="station")


class ChargingSession(Base):
    __tablename__ = "charging_sessions"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=_uuid_str)
    vehicle_id: Mapped[str] = mapped_column(UUID_STR, ForeignKey("vehicles.id", ondelete="SET NULL"), index=True, nullable=True)
    station_id: Mapped[Optional[str]] = mapped_column(UUID_STR, ForeignKey("charging_stations.id", ondelete="SET NULL"), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    energy_kwh: Mapped[Optional[float]] = mapped_column(Float)
    cost: Mapped[Optional[float]] = mapped_column(Float)

    vehicle: Mapped[Optional["Vehicle"]] = relationship("Vehicle", back_populates="charging_sessions")
    station: Mapped[Optional["ChargingStation"]] = relationship("ChargingStation", back_populates="charging_sessions")

    __table_args__ = (
        Index("ix_charge_vehicle_time", "vehicle_id", "start_time"),
    )


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=_uuid_str)
    vehicle_id: Mapped[Optional[str]] = mapped_column(UUID_STR, ForeignKey("vehicles.id", ondelete="SET NULL"), index=True)
    type: Mapped[str] = mapped_column(String(100), index=True)  # e.g., BatteryLow, Overheat, GeofenceBreach
    severity: Mapped[str] = mapped_column(String(20), index=True)  # INFO, WARN, CRITICAL
    message: Mapped[Optional[str]] = mapped_column(Text)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    vehicle: Mapped[Optional["Vehicle"]] = relationship("Vehicle", back_populates="alerts")


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=_uuid_str)
    vehicle_id: Mapped[str] = mapped_column(UUID_STR, ForeignKey("vehicles.id", ondelete="CASCADE"), index=True, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    task: Mapped[str] = mapped_column(String(100))  # e.g., "Maintenance", "Trip", "ChargingWindow"
    notes: Mapped[Optional[str]] = mapped_column(Text)

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="schedules")


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=_uuid_str)
    vehicle_id: Mapped[str] = mapped_column(UUID_STR, ForeignKey("vehicles.id", ondelete="CASCADE"), index=True, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    start_latitude: Mapped[Optional[float]] = mapped_column(Float)
    start_longitude: Mapped[Optional[float]] = mapped_column(Float)
    end_latitude: Mapped[Optional[float]] = mapped_column(Float)
    end_longitude: Mapped[Optional[float]] = mapped_column(Float)
    distance_km: Mapped[Optional[float]] = mapped_column(Float)
    avg_speed_kmh: Mapped[Optional[float]] = mapped_column(Float)

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="trips")

    __table_args__ = (
        Index("ix_trip_vehicle_time", "vehicle_id", "start_time"),
    )
