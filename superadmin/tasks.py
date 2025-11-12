from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def send_company_created_email(company):
    try:
        subject = 'Your company has been added to our website'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [company["email"]]

        html_content = render_to_string('admin_email_templates/added_company.html', {
            'company_name': company["name"],       
            'email': company["email"],
            'phone': company["phone1"],            
            'sender_mail': from_email
        })

        email = EmailMultiAlternatives(subject, '', from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        
        email.send()

        return "Sended Email"
    except Exception as e:
        logger.error(f'Error sending offer mail: {e}')