from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class NormalizedResource(BaseModel):
    resource_id: str
    resource_type: str
    service: str
    configuration: Dict[str, Any]

class FindingSchema(BaseModel):
    id: str
    severity: str
    service: str
    resource_id: str
    title: str
    description: str
    recommendation: str
    timestamp: datetime
    status: str
    
    class Config:
        from_attributes = True

class ScanResult(BaseModel):
    status: str
    findings_count: int

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str

class UserSchema(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class SettingSchema(BaseModel):
    key: str
    value: Optional[str] = None
    is_encrypted: bool

    class Config:
        from_attributes = True

class SettingCreate(BaseModel):
    key: str
    value: Optional[str] = None
    is_encrypted: Optional[bool] = False

class AccountCreate(BaseModel):
    name: str
    aws_account_id: str
    role_arn: str
    region: Optional[str] = "us-east-1"

class AccountSchema(BaseModel):
    id: int
    name: str
    aws_account_id: str
    role_arn: str
    region: str
    status: str
    last_scan_at: Optional[datetime] = None
    last_scan_status: Optional[str] = None
    last_error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TrustPolicyResponse(BaseModel):
    account_id: int
    external_id: str
    trust_policy: Dict[str, Any]
    read_only_policy: Dict[str, Any]
    instructions: str

