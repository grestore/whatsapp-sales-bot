# WhatsApp Sales Bot - Replit Setup Guide

## Overview

This is a Flask-based WhatsApp sales bot application that integrates with Twilio's WhatsApp API and OpenAI's GPT for automated sales conversations. The bot is designed to handle incoming WhatsApp messages, generate intelligent sales responses, and provide a dashboard for monitoring conversations and metrics.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with configurable database backend (SQLite by default, PostgreSQL support via environment variables)
- **Web Server**: Flask development server with proxy fix middleware for production deployment
- **Session Management**: Flask sessions with configurable secret key

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap (dark theme)
- **JavaScript**: Vanilla JavaScript with Bootstrap components
- **Icons**: Font Awesome
- **Charts**: Chart.js for analytics visualization

### External Services Integration
- **WhatsApp API**: Twilio WhatsApp Business API for message handling
- **AI Service**: OpenAI GPT for intelligent sales response generation
- **Webhook Handling**: Twilio webhook verification and message processing

## Key Components

### Core Application Files
- **app.py**: Main Flask application configuration and database setup
- **main.py**: Application entry point
- **models.py**: SQLAlchemy database models (Conversation, Message, SalesMetrics)
- **routes.py**: Flask route handlers for web interface and webhooks
- **whatsapp_service.py**: Twilio WhatsApp API integration service
- **openai_service.py**: OpenAI GPT integration for sales responses

### Database Models
- **Conversation**: Stores customer conversations with phone numbers and status tracking
- **Message**: Individual messages within conversations (incoming/outgoing)
- **SalesMetrics**: Daily metrics tracking for sales performance analysis

### User Interface
- **Dashboard**: Real-time conversation monitoring and metrics overview
- **Analytics**: Sales performance charts and historical data visualization
- **Responsive Design**: Bootstrap-based UI with dark theme

## Data Flow

1. **Incoming Messages**: WhatsApp messages arrive via Twilio webhook to `/whatsapp` endpoint
2. **Message Processing**: 
   - Verify webhook authenticity (optional)
   - Extract message content and sender information
   - Store message in database
   - Generate AI response using OpenAI service
3. **Response Generation**: OpenAI GPT processes conversation context and generates sales-focused responses in Spanish
4. **Outgoing Messages**: Send AI-generated responses back through Twilio WhatsApp API
5. **Metrics Update**: Track conversation and message counts for analytics

## External Dependencies

### Required Environment Variables
- `TWILIO_ACCOUNT_SID`: Twilio account identifier
- `TWILIO_AUTH_TOKEN`: Twilio authentication token
- `TWILIO_PHONE_NUMBER`: WhatsApp business phone number
- `OPENAI_API_KEY`: OpenAI API key for GPT integration
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)
- `SESSION_SECRET`: Flask session secret key (optional, defaults to dev key)

### Optional Configuration
- `TWILIO_WEBHOOK_URL`: Webhook URL for Twilio configuration
- `VERIFY_WEBHOOK`: Enable webhook verification (recommended for production)

### Third-Party Services
- **Twilio**: WhatsApp Business API integration
- **OpenAI**: GPT-based conversation AI
- **Bootstrap CDN**: UI framework and styling
- **Font Awesome CDN**: Icon library
- **Chart.js CDN**: Data visualization

## Deployment Strategy

### Development Environment
- Flask development server with debug mode enabled
- SQLite database for local development
- Environment variables loaded from local configuration

### Production Considerations
- **Proxy Configuration**: ProxyFix middleware configured for reverse proxy deployment
- **Database**: Environment-based database URL configuration supports PostgreSQL
- **Security**: Webhook verification and session secret management
- **Logging**: Comprehensive logging configuration for monitoring

### Scalability Features
- **Database Connection Pooling**: Configured with pool_recycle and pool_pre_ping
- **Session Management**: Stateless design with database-backed conversation tracking
- **Async Support**: Ready for async deployment with proper WSGI server

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- July 05, 2025. Initial setup