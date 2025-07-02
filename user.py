from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    user_id: str
    name: str
    role: str = "user"
    privileges: str = "basic"
    email: Optional[str] = None
    created_at: Optional[str] = None

# System user for ArielMatrix operations
SYSTEM_USER = User(
    user_id="ariel_system",
    name="Ariel System",
    role="system",
    privileges="all"
)

ARIEL_MATRIX_USER = User(
    user_id="ariel_matrix",
    name="ArielMatrix AI",
    role="ai_agent",
    privileges="autonomous"
)
