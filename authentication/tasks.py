from django.core.mail import send_mail
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_email(subject, message, from_email, recipient_list, fail_silently):
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently)
    except Exception as e:
        logger.exception(f"Error in send_email of authentication.tasks: {e}")