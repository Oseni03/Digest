from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_welcome_email(niche, to_email):
    """
    Sends welcome e-mail to subscribers

    :param to_email: subscribers email
    """
    context = {
        'archive_url': reverse("newsletter:archive"),
        'site_url': settings.NEWSLETTER_SITE_BASE_URL,
        'niche': niche,
    }

    # Send context so that users can use context data in the subject
    subject = render_to_string(
        'newsletter/email/email_welcome_subject.txt',
        context
    ).rstrip('\n')

    text_body = render_to_string(
        'newsletter/email/email_welcome.txt', 
        context
    )
    html_body = render_to_string(
        'newsletter/email/email_welcome.html', 
        context
    )

    message = EmailMultiAlternatives(
        subject, text_body, settings.EMAIL_HOST_USER, [to_email]
    )

    message.attach_alternative(html_body, 'text/html')
    message.send()
