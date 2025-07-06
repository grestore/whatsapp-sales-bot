from datetime import datetime
from app import db
from sqlalchemy import func

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    customer_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, closed, follow_up
    
    # Relationship to messages
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Conversation {self.phone_number}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    message_body = db.Column(db.Text, nullable=False)
    is_incoming = db.Column(db.Boolean, nullable=False)  # True for incoming, False for outgoing
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    twilio_sid = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Message {self.id}>'

class SalesMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    total_conversations = db.Column(db.Integer, default=0)
    leads_generated = db.Column(db.Integer, default=0)
    sales_closed = db.Column(db.Integer, default=0)
    total_messages = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<SalesMetrics {self.date}>'
