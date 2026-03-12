from telegram.ext import Application

def setup_scheduler(app: Application, chat_id: int):
    """
    Registers a weekly ESG update job for the given chat_id.
    Called from bot.py when user sends /start.
    """
    from bot import scheduled_check

    jobs = app.job_queue.get_jobs_by_name(str(chat_id))
    if not jobs:
        app.job_queue.run_repeating(
            scheduled_check,
            interval=60 * 60 * 24 * 7,
            first=10,
            chat_id=chat_id,
            name=str(chat_id),
        )
        return True
    return False