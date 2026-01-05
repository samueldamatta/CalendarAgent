from apscheduler.schedulers.background import BackgroundScheduler
from app.followup.tasks import check_for_notifications

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Executa a cada minuto
    scheduler.add_job(check_for_notifications, 'interval', minutes=1)
    scheduler.start()
    print("⏰ Scheduler iniciado (verificação a cada minuto)")
