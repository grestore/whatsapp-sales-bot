import os
import logging
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from flask import request
from models import Conversation, Message, SalesMetrics
from app import db
from datetime import datetime, date

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.phone_number = os.environ.get("TWILIO_PHONE_NUMBER")
        self.webhook_url = os.environ.get("TWILIO_WEBHOOK_URL")
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            logger.error("Missing required Twilio credentials")
            raise ValueError("Missing required Twilio credentials")
        
        self.client = Client(self.account_sid, self.auth_token)
        self.validator = RequestValidator(self.auth_token)
    
    def verify_webhook(self, url, params, signature):
        """Verify that the request came from Twilio"""
        try:
            return self.validator.validate(url, params, signature)
        except Exception as e:
            logger.error(f"Webhook verification failed: {e}")
            return False
    
    def get_or_create_conversation(self, phone_number):
        """Get existing conversation or create new one"""
        conversation = Conversation.query.filter_by(
            phone_number=phone_number,
            status='active'
        ).first()
        
        if not conversation:
            conversation = Conversation(phone_number=phone_number)
            db.session.add(conversation)
            db.session.commit()
            logger.info(f"Created new conversation for {phone_number}")
        
        return conversation
    
    def save_message(self, conversation_id, message_body, is_incoming, twilio_sid=None):
        """Save message to database"""
        message = Message(
            conversation_id=conversation_id,
            message_body=message_body,
            is_incoming=is_incoming,
            twilio_sid=twilio_sid
        )
        db.session.add(message)
        db.session.commit()
        
        # Update metrics
        self.update_daily_metrics()
        
        return message
    
    def send_message(self, to_number, message_body):
        """Send WhatsApp message via Twilio"""
        try:
            message = self.client.messages.create(
                body=message_body,
                from_=f"whatsapp:{self.phone_number}",
                to=f"whatsapp:{to_number}"
            )
            logger.info(f"Message sent to {to_number}: SID {message.sid}")
            return message.sid
        except Exception as e:
            logger.error(f"Failed to send message to {to_number}: {e}")
            raise
    
    def create_twiml_response(self, message_body):
        """Create TwiML response for webhook"""
        response = MessagingResponse()
        msg = response.message()
        msg.body(message_body)
        return str(response)
    
    def update_daily_metrics(self):
        """Update daily sales metrics"""
        today = date.today()
        metrics = SalesMetrics.query.filter_by(date=today).first()
        
        if not metrics:
            metrics = SalesMetrics(date=today)
            db.session.add(metrics)
        
        # Update metrics
        metrics.total_conversations = Conversation.query.filter(
            db.func.date(Conversation.created_at) == today
        ).count()
        
        metrics.total_messages = Message.query.filter(
            db.func.date(Message.timestamp) == today
        ).count()
        
        db.session.commit()
    
    def get_conversation_history(self, conversation_id, limit=10):
        """Get recent messages for conversation context"""
        messages = Message.query.filter_by(conversation_id=conversation_id)\
            .order_by(Message.timestamp.desc())\
            .limit(limit).all()
        
        return list(reversed(messages))
