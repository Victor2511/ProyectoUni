# tasks.py
from django.core.mail import send_mail

def send_email_task(subject, message, recipient_list):
    """
    Enviar correos electrónicos de forma asíncrona utilizando Django-Q.
    """
    send_mail(
        subject,
        message,
        'victorgabrieljunior@gmail.com',  # Remitente
        recipient_list,
        fail_silently=False
    )
