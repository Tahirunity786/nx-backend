from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_nx_email(client_email, client_name="Valued User"):
    """
    Sends a welcome email to the specified client.
    
    Args:
        client_email (str): The recipient's email address.
        client_name (str): The recipient's name (default: "Valued User").
    
    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    try:
        # Email subject and sender
        subject = "NX Craft - Thanks for contacting with us."
        sender_email = settings.EMAIL_HOST_USER  # Use Django's email configuration

        # Render email content with dynamic variables
        html_content = render_to_string("emails/contact.html", {
            "client_name": client_name,
            "logo_url": "https://sitif62914q.pythonanywhere.com/static/media/nx-craft.webp",
            "website_url": "https://www.nxcraft.com",
        })

        # Create and send the email
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=sender_email,
            to=[client_email],
        )
        email.content_subtype = "html"  # Specify HTML content
        email.send(fail_silently=False)

        logger.info(f"Email sent successfully to {client_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {client_email}: {str(e)}", exc_info=True)
        return False
