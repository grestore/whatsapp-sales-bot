import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("Missing OpenAI API key")
            raise ValueError("Missing OpenAI API key")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Sales system prompt in Spanish
        self.sales_prompt = """
        Eres un vendedor experto y amigable especializado en ventas por WhatsApp. Tu objetivo es:

        1. Ser cálido y cercano en tu comunicación
        2. Identificar las necesidades del cliente
        3. Presentar soluciones de valor
        4. Generar confianza y credibilidad
        5. Guiar hacia el cierre de la venta
        6. Mantener un tono profesional pero accesible

        REGLAS IMPORTANTES:
        - Siempre responde en español
        - Mantén las respuestas concisas (máximo 2-3 oraciones)
        - Haz preguntas para entender mejor las necesidades
        - Usa emojis ocasionalmente para ser más amigable
        - Si no tienes información específica sobre productos, enfócate en generar interés y solicitar contacto
        - Intenta obtener información de contacto (nombre, email, teléfono)
        - Proporciona valor en cada interacción

        Contexto de la conversación: Eres un asistente de ventas que ayuda a los clientes a encontrar productos y servicios que necesitan.
        """
    
    def generate_sales_response(self, incoming_message, conversation_context=None):
        """Generate sales-focused response using OpenAI GPT"""
        try:
            # Build conversation context
            messages = [
                {"role": "system", "content": self.sales_prompt}
            ]
            
            # Add conversation history if available
            if conversation_context:
                for msg in conversation_context:
                    role = "user" if msg.is_incoming else "assistant"
                    messages.append({"role": role, "content": msg.message_body})
            
            # Add current message
            messages.append({"role": "user", "content": incoming_message})
            
            # Generate response using gpt-4o
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            reply = response.choices[0].message.content.strip()
            logger.info(f"Generated OpenAI response: {reply}")
            
            return reply
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            # Fallback response in Spanish
            return "¡Hola! Gracias por contactarnos. En este momento tenemos un problema técnico, pero te responderemos pronto. ¿Podrías dejarme tu nombre y en qué te puedo ayudar? 😊"
    
    def analyze_intent(self, message):
        """Analyze customer intent for better sales routing"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Analiza el intent del mensaje del cliente y clasifícalo. "
                        "Responde con JSON en este formato: "
                        "{'intent': 'categoria', 'confidence': 0.8, 'keywords': ['palabra1', 'palabra2']} "
                        "Las categorías pueden ser: 'consulta_producto', 'precio', 'soporte', 'compra', 'saludo', 'otro'"
                    },
                    {"role": "user", "content": message}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            return {"intent": "otro", "confidence": 0.5, "keywords": []}
    
    def generate_lead_summary(self, conversation_messages):
        """Generate a summary of the conversation for sales follow-up"""
        try:
            # Prepare conversation text
            conversation_text = ""
            for msg in conversation_messages:
                role = "Cliente" if msg.is_incoming else "Vendedor"
                conversation_text += f"{role}: {msg.message_body}\n"
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Analiza esta conversación de ventas y genera un resumen ejecutivo. "
                        "Incluye: necesidades del cliente, productos mencionados, nivel de interés, "
                        "próximos pasos recomendados. Responde en español."
                    },
                    {"role": "user", "content": conversation_text}
                ],
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Lead summary generation failed: {e}")
            return "Error al generar resumen"
