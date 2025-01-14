from typing import Optional

from twilio.rest import Client


class WhatsAppService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WhatsAppService, cls).__new__(cls)

        return cls._instance

    async def send_whatsapp_message(
        self,
        to_number: str,
        message_body: str,
        media_url: Optional[str] = None,
        account_sid: str = "your_account_sid",
        auth_token: str = "your_auth_token",
        from_number: str = "your_twilio_whatsapp_number",
    ) -> dict:
        """
        Send a WhatsApp message using Twilio.

        Args:
            to_number (str): Recipient's phone number in E.164 format (e.g., '+1234567890')
            message_body (str): Content of the message
            media_url (str, optional): URL of media to send (image, PDF, etc.)
            account_sid (str): Your Twilio Account SID
            auth_token (str): Your Twilio Auth Token
            from_number (str): Your Twilio WhatsApp number

        Returns:
            dict: Twilio message response object

        Raises:
            TwilioRestException: If message sending fails
        """
        # Initialize Twilio client
        client = Client(account_sid, auth_token)

        # Ensure the to_number is in WhatsApp format
        to_whatsapp_number = f"whatsapp:{to_number}"
        from_whatsapp_number = f"whatsapp:{from_number}"

        try:
            # Create message parameters
            message_params = {"from_": from_whatsapp_number, "body": message_body, "to": to_whatsapp_number}

            # Add media URL if provided
            if media_url:
                message_params["media_url"] = [media_url]

            # Send message
            message = client.messages.create(**message_params)

            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status,
                "error_code": message.error_code,
                "error_message": message.error_message,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
