
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


def send_email(toEmail):

    context = {
        'name': 'test'
    }

    email_subject = 'Test Subject'
    email_body = render_to_string('bupaBooking/email.txt', context)

    email = EmailMessage(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL, [toEmail, ],
    )
    email.send(fail_silently=False)
