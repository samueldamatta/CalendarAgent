import json
import os
import datetime
from openai import OpenAI
from app.tool.google_calendar import GoogleCalendarClient
from app.database.mongodb import db_manager
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
calendar = GoogleCalendarClient()

def get_calendar_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "think",
                "description": "Use esta ferramenta para raciocinar, planejar os próximos passos ou analisar informações antes de tomar uma ação.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "thought": {
                            "type": "string",
                            "description": "O seu raciocínio interno ou plano de ação.",
                        },
                    },
                    "required": ["thought"],
                },
            },
        },
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

def process_message(user_id: str, user_message: str):
    current_date = datetime.date.today().isoformat()
    
    # Busca o histórico do banco
    history = db_manager.get_history(user_id)
    
    system_message = {"role": "system", "content": f"""Você é um assistente de agendamento do Samuel. 
        Hojé é {current_date}. 
        Seu objetivo é marcar reuniões no Google Calendar.
        
        Você tem uma ferramenta chamada 'think'. Use-a SEMPRE antes de agendar algo complexo ou quando precisar organizar seu raciocínio.
        
        Siga EXATAMENTE estes passos:
        1. Se a solicitação for complexa, use 'think' para planejar.
        2. Sempre verifique a disponibilidade usando 'check_availability' antes de qualquer outra coisa.
        3. Se o horário solicitado estiver livre, use 'book_appointment' para marcar.
        4. Se estiver ocupado, sugira outro serviço/horário.
        
        Responda sempre em Português de forma gentil e curta.
        Importante: Os agendamentos são feitos no fuso horário America/Sao_Paulo (Brasília)."""}

    messages = [system_message] + history + [{"role": "user", "content": user_message}]

    # Salva a mensagem do usuário no histórico
    db_manager.save_message(user_id, {"role": "user", "content": user_message})

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=get_calendar_tools(),
            tool_choice="auto",
        )

        response_message = response.choices[0].message
        
        # Converte o objeto de mensagem da OpenAI para um formato serializável (dict) para salvar no banco
        msg_dict = {
            "role": "assistant",
            "content": response_message.content,
        }
        if response_message.tool_calls:
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in response_message.tool_calls
            ]

        tool_calls = response_message.tool_calls

        if not tool_calls:
            # Salva a resposta final do assistente no histórico
            db_manager.save_message(user_id, msg_dict)
            return response_message.content

        messages.append(response_message)
        # Salva a mensagem que chamou a ferramenta no histórico
        db_manager.save_message(user_id, msg_dict)
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"--- Agent calling tool: {function_name}")
            
            result = ""
            if function_name == "think":
                thought = function_args.get("thought")
                print(f"💭 PENSAMENTO: {thought}")
                result = "Pensamento registrado. Continue sua análise."
            elif function_name == "check_availability":
                result = calendar.check_availability(function_args.get("date"))
            elif function_name == "book_appointment":
                result = calendar.create_event(
                    summary=function_args.get("summary"),
                    start_time=function_args.get("start_time"),
                    end_time=function_args.get("end_time"),
                    description=function_args.get("description", "")
                )
                if result:
                    event_id = result.get('id')
                    html_link = result.get('htmlLink')
                    
                    # Salva o agendamento para notificações futuras
                    appointment_info = {
                        "user_id": user_id,
                        "event_id": event_id,
                        "summary": function_args.get("summary"),
                        "start_time": function_args.get("start_time"),
                        "end_time": function_args.get("end_time"),
                        "reminder_sent": False,
                        "follow_up_sent": False,
                        "created_at": datetime.datetime.utcnow().isoformat()
                    }
                    db_manager.save_appointment(appointment_info)
                    print(f"💾 Agendamento salvo no banco para notificações: {summary} ({start_time})")
                    
                    result = f"Agendamento confirmado: {html_link}"
                else:
                    result = "Erro ao realizar o agendamento."
            
            print(f"--- Tool output: {result}")
            
            tool_result_msg = {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": str(result),
            }
            messages.append(tool_result_msg)
            # Salva o resultado da ferramenta no histórico
            db_manager.save_message(user_id, tool_result_msg)
