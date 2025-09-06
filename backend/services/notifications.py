"""
WhatsApp notification service using Twilio
"""
import os
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Try to import Twilio, but make it optional
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
    logger.info("✅ Twilio library imported successfully")
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("⚠️ Twilio not installed. Install with: pip install twilio")
    print("⚠️ Twilio not installed. WhatsApp notifications will be disabled.")

def send_whatsapp_notification(user_phone_number: str, tracker_name: str, new_status: str) -> bool:
    """
    Sends a WhatsApp notification using Twilio if available and configured.
    
    Args:
        user_phone_number: Phone number in E.164 format (e.g., +919876543210)
        tracker_name: Name of the tracker that was updated
        new_status: The new status message
        
    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Check if Twilio is available
    if not TWILIO_AVAILABLE:
        logger.warning(f"📵 [{timestamp}] Skipping WhatsApp notification - Twilio not installed")
        print(f"📵 [{timestamp}] Skipping WhatsApp notification - Twilio not installed")
        return False
    
    # Get credentials from environment variables
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
    TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")
    
    # Check if credentials are configured
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER]):
        logger.warning(f"📵 [{timestamp}] Skipping WhatsApp notification - Twilio credentials not configured")
        print(f"📵 [{timestamp}] Skipping WhatsApp notification - Twilio credentials not configured")
        return False
    
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Create the message body
        message_body = f"🚀 Universal Scraper Alert!\n\nYour tracker *'{tracker_name}'* has a new status:\n\n*{new_status}*\n\nTime: {timestamp}"
        
        logger.info(f"📱 [{timestamp}] Sending WhatsApp to {user_phone_number}")
        print(f"📱 [{timestamp}] Sending WhatsApp to {user_phone_number}")
        
        # Send the WhatsApp message
        message = client.messages.create(
            from_=f'whatsapp:{TWILIO_WHATSAPP_NUMBER}',
            body=message_body,
            to=f'whatsapp:{user_phone_number}'
        )
        
        logger.info(f"✅ [{timestamp}] WhatsApp notification sent successfully")
        print(f"✅ WhatsApp notification sent successfully to {user_phone_number}")
        return True
        
    except Exception as e:
        logger.error(f"❌ [{timestamp}] Error sending WhatsApp notification: {e}")
        print(f"❌ Error sending WhatsApp notification: {e}")
        return False
