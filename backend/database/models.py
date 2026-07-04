from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from backend.database.session import Base
from datetime import datetime


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    name = Column(String, nullable=False)

    aws_account_id = Column(String, unique=True, index=True, nullable=False)

    role_arn = Column(String, nullable=False)

    external_id = Column(String, nullable=False)

    region = Column(String, default="us-east-1")

    status = Column(String, default="PENDING")

    last_scan_at = Column(DateTime)

    last_scan_status = Column(String)

    last_error = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    assets = relationship("Asset", back_populates="account", cascade="all, delete-orphan")

    findings = relationship("Finding", back_populates="account", cascade="all, delete-orphan")

    scans = relationship("ScanHistory", back_populates="account", cascade="all, delete-orphan")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    account_id = Column(Integer, ForeignKey("accounts.id"))

    service = Column(String, index=True)

    resource_type = Column(String, index=True)

    resource_id = Column(String, index=True)

    arn = Column(String)

    name = Column(String)

    region = Column(String)

    tags = Column(JSON, default={})

    configuration = Column(JSON, default={})

    status = Column(String, default="ACTIVE")


    risk_score = Column(Integer, default=0)

    compliance_status = Column(String, default="UNKNOWN")

    owner = Column(String)

    environment = Column(String)

    business_criticality = Column(String, default="MEDIUM")

    relationships = Column(JSON, default={})

    first_seen = Column(DateTime, default=datetime.utcnow)

    last_seen = Column(DateTime, default=datetime.utcnow)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    account = relationship("Account", back_populates="assets")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String, primary_key=True, index=True)

    account_id = Column(Integer, ForeignKey("accounts.id"))

    severity = Column(String, index=True)

    service = Column(String, index=True)

    resource_id = Column(String, index=True)

    title = Column(String)

    description = Column(String)

    recommendation = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)

    status = Column(String, default="ACTIVE")

    first_seen = Column(DateTime, default=datetime.utcnow)

    last_seen = Column(DateTime, default=datetime.utcnow)

    resolved_at = Column(DateTime, nullable=True)

    


    risk_score = Column(Integer, default=0)

    compliance_status = Column(String, default="UNKNOWN")

    owner = Column(String)

    environment = Column(String)

    business_criticality = Column(String, default="MEDIUM")

    relationships = Column(JSON, default={})

    account = relationship("Account", back_populates="findings")


class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    account_id = Column(Integer, ForeignKey("accounts.id"))

    timestamp = Column(DateTime, default=datetime.utcnow)

    findings_count = Column(Integer)

    status = Column(String)

    error_message = Column(String)

    resources_scanned = Column(Integer, default=0)

    provider = Column(String, default="gcp")

    critical = Column(Integer, default=0)

    high = Column(Integer, default=0)

    medium = Column(Integer, default=0)

    low = Column(Integer, default=0)

    duration_seconds = Column(Integer, default=0)

    account = relationship("Account", back_populates="scans")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    username = Column(String, unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True, index=True)

    value = Column(String)

    is_encrypted = Column(Boolean, default=False)