import datetime
from app.database.mongodb import db_manager
from app.webhook.evolution_api import send_whatsapp_message
from dateutil import parser
import pytz

# Configuração do fuso horário
TZ = pytz.timezone("America/Sao_Paulo")

def check_for_notifications():
    """
    Verifica agendamentos pendentes de lembrete (30 min antes) 
    ou follow-up (5 min depois).
    """
    now = datetime.datetime.now(TZ)
    pending = db_manager.get_pending_notifications()
    
    if not pending:
        # Silencioso se não houver nada pendente para não poluir o log
        return

    print(f"⏰ Verificando {len(pending)} agendamentos pendentes em {now.strftime('%H:%M:%S')}")
    
    for appt in pending:
        try:
            start_time = parser.isoparse(appt["start_time"])
            end_time = parser.isoparse(appt["end_time"])
            
            # Garantir que os horários tenham fuso horário para comparação
            if start_time.tzinfo is None:
                start_time = TZ.localize(start_time)
            elif start_time.tzinfo != TZ:
                # Se vier com Z ou outro fuso, converte para o fuso local
                start_time = start_time.astimezone(TZ)

            if end_time.tzinfo is None:
                end_time = TZ.localize(end_time)
            elif end_time.tzinfo != TZ:
                end_time = end_time.astimezone(TZ)

            user_id = appt["user_id"]
            event_id = appt["event_id"]
            summary = appt["summary"]

            # Lembrete: 30 minutos antes do início
            reminder_time = start_time - datetime.timedelta(minutes=30)
            
            # Debug log comentado (pode ativar se necessário)
            # print(f"Checking '{summary}': Reminder target: {reminder_time.strftime('%H:%M')}, Follow-up target: {(end_time + datetime.timedelta(minutes=5)).strftime('%H:%M')}")

            if not appt.get("reminder_sent") and now >= reminder_time and now < start_time:
                message = f"🔔 *Lembrete:* Sua reunião '{summary}' começa em 30 minutos!"
                print(f"🚀 Enviando lembrete para {user_id}: {summary}")
                send_whatsapp_message(user_id, message)
                db_manager.mark_notification_sent(event_id, "reminder")

            # Follow-up: 5 minutos depois do término
            follow_up_time = end_time + datetime.timedelta(minutes=5)
            if not appt.get("follow_up_sent") and now >= follow_up_time:
                message = f"👋 Olá! Sua reunião '{summary}' terminou. Como foi? Se precisar de algo, estou aqui."
                print(f"🚀 Enviando follow-up para {user_id}: {summary}")
                send_whatsapp_message(user_id, message)
                db_manager.mark_notification_sent(event_id, "follow_up")
                
        except Exception as e:
            print(f"Erro ao processar notificação para evento {appt.get('event_id')}: {e}")
