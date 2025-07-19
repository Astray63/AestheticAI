from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    pin: str
    full_name: str
    speciality: str
    license_number: str


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    speciality: str
    is_active: bool
    created_at: datetime


class PatientCreate(BaseModel):
    age_range: str
    gender: str
    skin_type: str


class PatientResponse(BaseModel):
    id: int
    anonymous_id: str
    age_range: str
    gender: str
    skin_type: str
    created_at: datetime


class SimulationRequest(BaseModel):
    patient_id: int
    intervention_type: str
    dose: float
    parameters: Optional[Dict[str, Any]] = {}


class SimulationResponse(BaseModel):
    id: int
    patient_id: int
    intervention_type: str
    dose: float
    status: str
    original_image_path: Optional[str]
    generated_image_path: Optional[str]
    generation_time: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]


class InterventionInfo(BaseModel):
    name: str
    min_dose: float
    max_dose: float
    unit: str


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    pin: str
