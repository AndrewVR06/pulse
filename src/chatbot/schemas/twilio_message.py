from pydantic import BaseModel, ConfigDict, Field

from chatbot.schemas.user_session import UserSession


class TwilioMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    body: str = Field(..., alias="Body")
    num_segments: str = Field(..., alias="NumSegments")
    # direction: Literal["inbound", "outbound-api", "outbound-call", "outbound-reply"] = Field(..., alias="Direction")
    from_number: str = Field(..., alias="From")
    to_number: str = Field(..., alias="To")
    whatsapp_id: str = Field(..., alias="WaId")
    account_sid: str = Field(..., alias="AccountSid")
    message_sid: str = Field(..., alias="MessageSid")
    profile_name: str = Field(..., alias="ProfileName")
    message_type: str = Field(..., alias="MessageType")

    user_session: UserSession | None = None
