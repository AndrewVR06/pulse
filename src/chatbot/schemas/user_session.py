from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PulsebotAnswer(BaseModel):
    model_config = ConfigDict(frozen=True)

    role: str
    content: str


class UserSession(BaseModel):
    model_config = ConfigDict(frozen=True)

    account_sid: str
    dialogue_answers: Optional[List[str]] = Field(default_factory=list)

    initiated_pulsebot: bool = False
    pulsebot_answers: Optional[List[PulsebotAnswer]] = Field(default_factory=list)

    @classmethod
    def empty(cls, account_sid) -> "UserSession":
        return UserSession(account_sid=account_sid)
