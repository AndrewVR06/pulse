from fastapi import APIRouter, Request, Response
from urllib.parse import parse_qs
from twilio.twiml.messaging_response import MessagingResponse

from chatbot.dialogues.base_dialogue import BaseDialogue
from chatbot.schemas.twilio_message import TwilioMessage
from services.redis_service import RedisService

chatbot_router = APIRouter(prefix="/chatbot", tags=["chatbot"])
redis_service = RedisService()


@chatbot_router.post("/message/")
async def receive_message(request: Request):
    payload: bytes = await request.body()
    decoded_payload = payload.decode("utf-8")

    # The body is a query encoded string, so we need to break it down into a dictionary
    # Ex. SmsMessageSid=SM2e9510c514d3d9cac8c81384faf7fc65&NumMedia=0&ProfileName=Andrew+Van+Rensburg&...
    parsed_data = {k: v[0] for k, v in parse_qs(decoded_payload).items()}
    message = TwilioMessage.model_validate(parsed_data)
    message.user_session = await redis_service.get_chatbot_session(message.account_sid)

    current_dialogue = await BaseDialogue(message).get_current_dialogue()
    message_answer = await current_dialogue.get_response()

    resp = MessagingResponse()
    resp.message(message_answer, to=message.from_number, from_=message.to_number)

    return Response(content=str(resp), media_type="application/xml")
