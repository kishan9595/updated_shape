from django.template.loader import get_template
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

def send_email(to_email,template_data):
    htmly = get_template('email_client.html')
    subject, from_email, to = 'New CLient', settings.EMAIL_HOST_USER, to_email
    html_content = htmly.render(template_data)
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return True

