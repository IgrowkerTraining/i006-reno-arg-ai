from pydantic import BaseModel
from typing import Optional, Union
from .body import BodyBase


class SystemMessage(BaseModel):
    role: str = "system"
    content: str


class UserMessage(BaseModel):
    role: str = "user"
    content: Optional[Union[str, BodyBase]] = None  # ← BodyBase usada acá


class PromptSchema(BaseModel):
    model: Optional[str] = None
    temperature: Optional[float] = None
    messages: list[Union[SystemMessage, UserMessage]]