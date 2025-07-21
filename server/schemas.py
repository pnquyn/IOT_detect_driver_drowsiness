from pydantic import BaseModel

class LogInput(BaseModel):
    driver_id: str
    drowsy_score: float
    led: bool
    buzzer: bool

class UserCreate(BaseModel):
    username: str
    password: str
