import json
import os
import datetime
from openai import OpenAI
from google_calendar import GoogleCalendarClient
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
calendar = GoogleCalendarClient()

def get_calendar_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "check_availability",
                "description": "Verifica a disponibilidade de horários para uma data específica.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "A data no formato YYYY-MM-DD",
                        },
                    },
                    "required": ["date"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "book_appointment",
                "description": "Agenda um compromisso no calendário.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "O título do agendamento (ex: Consulta com Samuel)",
                        },
                        "start_time": {
                            "type": "string",
                            "description": "O horário de início no formato ISO 8601 (ex: 2024-05-15T14:00:00Z)",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "O horário de término no formato ISO 8601 (ex: 2024-05-15T15:00:00Z)",
                        },
                        "description": {
                            "type": "string",
                            "description": "Uma breve descrição do agendamento",
                        },
                    },
                    "required": ["summary", "start_time", "end_time"],
                },
            },
        },
    ]

def process_message(user_message: str):
    current_date = datetime.date.today().isoformat()
    messages = [
        {"role": "system", "content": f"""Você é um assistente de agendamento do Samuel. 
        Hojé é {current_date}. 
        Seu objetivo é marcar reuniões no Google Calendar.
        Siga EXATAMENTE estes passos:
        1. Sempre verifique a disponibilidade usando 'check_availability' antes de qualquer outra coisa.
        2. Se o horário solicitado estiver livre, use 'book_appointment' para marcar.
        3. Se estiver ocupado, sugira outro serviço/horário.
        Responda sempre em Português de forma gentil e curta.
        Importante: Os agendamentos são feitos no fuso horário America/Sao_Paulo (Brasília)."""},
        {"role": "user", "content": user_message},
    ]

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=get_calendar_tools(),
            tool_choice="auto",
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if not tool_calls:
            return response_message.content

        messages.append(response_message)
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"--- Agent calling tool: {function_name} with {function_args}")
            
            if function_name == "check_availability":
                result = calendar.check_availability(function_args.get("date"))
            elif function_name == "book_appointment":
                result = calendar.create_event(
                    summary=function_args.get("summary"),
                    start_time=function_args.get("start_time"),
                    end_time=function_args.get("end_time"),
                    description=function_args.get("description", "")
                )
                if result:
                    result = f"Agendamento confirmado: {result.get('htmlLink')}"
                else:
                    result = "Erro ao realizar o agendamento."
            
            print(f"--- Tool output: {result}")
            
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": str(result),
            })
        
        # O loop continua para permitir que o modelo tome outra ação baseada no resultado da ferramenta
