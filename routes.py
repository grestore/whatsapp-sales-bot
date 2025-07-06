from flask import request, render_template, jsonify, redirect, url_for, flash
from app import app, db
from models import Conversation, Message, SalesMetrics
from whatsapp_service import WhatsAppService
from openai_service import OpenAIService
from datetime import datetime, date, timedelta
import logging
import os

logger = logging.getLogger(__name__)

# Initialize services
whatsapp_service = WhatsAppService()
openai_service = OpenAIService()

@app.route('/')
def dashboard():
    """Main dashboard view"""
    # Get recent conversations
    recent_conversations = Conversation.query.order_by(Conversation.updated_at.desc()).limit(10).all()
    
    # Get today's metrics
    today = date.today()
    today_metrics = SalesMetrics.query.filter_by(date=today).first()
    
    # Get weekly metrics
    week_ago = today - timedelta(days=7)
    weekly_metrics = SalesMetrics.query.filter(SalesMetrics.date >= week_ago).all()
    
    # Calculate totals
    total_conversations = sum(m.total_conversations for m in weekly_metrics)
    total_messages = sum(m.total_messages for m in weekly_metrics)
    
    return render_template('dashboard.html',
                         conversations=recent_conversations,
                         today_metrics=today_metrics,
                         total_conversations=total_conversations,
                         total_messages=total_messages)

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages"""
    try:
        # Get request data
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '').replace('whatsapp:', '')
        message_sid = request.values.get('MessageSid', '')
        
        # Verify webhook (optional but recommended for production)
        if os.environ.get('VERIFY_WEBHOOK', 'false').lower() == 'true':
            signature = request.headers.get('X-Twilio-Signature', '')
            if not whatsapp_service.verify_webhook(request.url, request.form, signature):
                logger.warning("Webhook verification failed")
                return "Unauthorized", 401
        
        logger.info(f"Received message from {from_number}: {incoming_msg}")
        
        if not incoming_msg:
            return "No message body", 400
        
        # Get or create conversation
        conversation = whatsapp_service.get_or_create_conversation(from_number)
        
        # Save incoming message
        whatsapp_service.save_message(
            conversation.id,
            incoming_msg,
            is_incoming=True,
            twilio_sid=message_sid
        )
        
        # Get conversation context for better responses
        conversation_context = whatsapp_service.get_conversation_history(conversation.id)
        
        # Generate AI response
        ai_response = openai_service.generate_sales_response(incoming_msg, conversation_context)
        
        # Save outgoing message
        whatsapp_service.save_message(
            conversation.id,
            ai_response,
            is_incoming=False
        )
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Return TwiML response
        return whatsapp_service.create_twiml_response(ai_response)
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {e}")
        # Return fallback response
        fallback_msg = "¡Hola! Gracias por contactarnos. Estamos experimentando problemas técnicos, pero te responderemos pronto. 😊"
        return whatsapp_service.create_twiml_response(fallback_msg)

@app.route('/conversation/<int:conversation_id>')
def view_conversation(conversation_id):
    """View detailed conversation"""
    conversation = Conversation.query.get_or_404(conversation_id)
    messages = Message.query.filter_by(conversation_id=conversation_id)\
        .order_by(Message.timestamp.asc()).all()
    
    return render_template('conversation_detail.html',
                         conversation=conversation,
                         messages=messages)

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    # Get metrics for the last 30 days
    thirty_days_ago = date.today() - timedelta(days=30)
    metrics = SalesMetrics.query.filter(SalesMetrics.date >= thirty_days_ago)\
        .order_by(SalesMetrics.date.desc()).all()
    
    # Calculate summary statistics
    total_conversations = sum(m.total_conversations for m in metrics)
    total_messages = sum(m.total_messages for m in metrics)
    
    # Active conversations
    active_conversations = Conversation.query.filter_by(status='active').count()
    
    return render_template('analytics.html',
                         metrics=metrics,
                         total_conversations=total_conversations,
                         total_messages=total_messages,
                         active_conversations=active_conversations)

@app.route('/api/send-message', methods=['POST'])
def send_message():
    """Send manual message to customer"""
    try:
        data = request.json
        phone_number = data.get('phone_number')
        message_body = data.get('message')
        
        if not phone_number or not message_body:
            return jsonify({'error': 'Phone number and message required'}), 400
        
        # Send message
        message_sid = whatsapp_service.send_message(phone_number, message_body)
        
        # Get or create conversation
        conversation = whatsapp_service.get_or_create_conversation(phone_number)
        
        # Save message
        whatsapp_service.save_message(
            conversation.id,
            message_body,
            is_incoming=False,
            twilio_sid=message_sid
        )
        
        return jsonify({'success': True, 'message_sid': message_sid})
        
    except Exception as e:
        logger.error(f"Error sending manual message: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations')
def api_conversations():
    """Get conversations data for dashboard"""
    conversations = Conversation.query.order_by(Conversation.updated_at.desc()).limit(20).all()
    
    data = []
    for conv in conversations:
        last_message = Message.query.filter_by(conversation_id=conv.id)\
            .order_by(Message.timestamp.desc()).first()
        
        data.append({
            'id': conv.id,
            'phone_number': conv.phone_number,
            'customer_name': conv.customer_name,
            'updated_at': conv.updated_at.isoformat(),
            'status': conv.status,
            'last_message': last_message.message_body if last_message else None,
            'message_count': len(conv.messages)
        })
    
    return jsonify(data)

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error="Página no encontrada"), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return render_template('error.html', error="Error interno del servidor"), 500
