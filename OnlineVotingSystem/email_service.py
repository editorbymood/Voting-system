import os
import logging
import socket
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get SendGrid API key from environment
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

# Use admin@yourdomain.com as the default sender if you've verified this domain in SendGrid
# For testing, we'll use the hostname plus example.com domain
host_name = socket.gethostname()
DEFAULT_FROM_EMAIL = os.environ.get('FROM_EMAIL', f'admin@{host_name}.example.com')

# Base URL for the application - used in email templates
# In production, this should be the actual domain
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')

# Check if we're in development/test mode
IS_DEVELOPMENT = 'development' in os.environ.get('FLASK_ENV', '') or 'test' in os.environ.get('FLASK_ENV', '') or 'localhost' in BASE_URL

# Check if email functionality is available
EMAIL_ENABLED = bool(SENDGRID_API_KEY)

if not EMAIL_ENABLED:
    logger.warning("SendGrid API key is not set. Email functionality will be disabled.")
else:
    if IS_DEVELOPMENT:
        logger.info(f"Email functionality is enabled with SendGrid in DEVELOPMENT mode. Using sender: {DEFAULT_FROM_EMAIL}")
        logger.info("In development mode, emails will be logged but not actually sent unless SENDGRID_FORCE_SEND=true")
    else:
        logger.info(f"Email functionality is enabled with SendGrid in PRODUCTION mode. Using sender: {DEFAULT_FROM_EMAIL}")
        logger.info("NOTE: In production, make sure to verify your sender domain in SendGrid.")

def send_email(to_email, subject, html_content=None, text_content=None):
    """
    Send an email using SendGrid API
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        html_content (str, optional): HTML content of the email
        text_content (str, optional): Plain text content of the email
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Skip email sending if not enabled
    if not EMAIL_ENABLED:
        logger.info(f"Email would be sent to {to_email} with subject '{subject}' (skipped - email disabled)")
        return False
        
    if not html_content and not text_content:
        logger.error("Either html_content or text_content must be provided")
        return False
        
    # Use html_content by default, fall back to text_content
    content_type = "text/html" if html_content else "text/plain"
    content_body = html_content if html_content else text_content
    
    # Log the email content for debugging and as a fallback
    logger.info(f"Preparing to send email to {to_email} with subject '{subject}'")
    
    # If we're in development/testing environment, just log the email content
    if IS_DEVELOPMENT and not os.environ.get('SENDGRID_FORCE_SEND'):
        logger.info(f"Email content would be sent (development mode):\nTo: {to_email}\nSubject: {subject}\nContent: (length: {len(content_body)} chars)")
        # Return True in development to simulate successful sending
        return True
    
    # Production environment - actually send the email
    try:
        message = Mail(
            from_email=Email(DEFAULT_FROM_EMAIL),
            to_emails=To(to_email),
            subject=subject,
            html_content=Content(content_type, content_body)
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Email sent to {to_email}, status code: {response.status_code}")
        return True
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error sending email: {error_msg}")
        
        # Special handling for sender identity verification errors
        if "sender identity" in error_msg.lower() or "403" in error_msg:
            logger.warning("Sender identity verification error. In production, please verify your domain in SendGrid.")
            # In development/testing, we'll consider this a "soft failure" and still return True
            if IS_DEVELOPMENT:
                logger.info("Development mode: treating email as sent despite verification error")
                return True
                
        return False

def send_registration_confirmation(username, email):
    """Send welcome email to newly registered users"""
    subject = "Welcome to Online Voting System"
    login_url = f"{BASE_URL}/login"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
        <h2 style="color: #4a5568; text-align: center;">Welcome to the Online Voting System!</h2>
        <p style="color: #4a5568; font-size: 16px;">Hello {username},</p>
        <p style="color: #4a5568; font-size: 16px;">Thank you for registering with our Online Voting System. Your account has been successfully created.</p>
        <p style="color: #4a5568; font-size: 16px;">You can now log in using your email address and the password you provided during registration.</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{login_url}" style="background-color: #4299e1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Log In Now</a>
        </div>
        <p style="color: #4a5568; font-size: 16px;">If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
        <p style="color: #4a5568; font-size: 16px;">Thank you for participating in the democratic process!</p>
        <p style="color: #4a5568; font-size: 14px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 15px;">
            Regards,<br>
            The Online Voting System Team
        </p>
    </div>
    """
    return send_email(email, subject, html_content=html_content)

def send_login_notification(username, email):
    """Send login notification email"""
    subject = "Login Notification - Online Voting System"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
        <h2 style="color: #4a5568; text-align: center;">Login Notification</h2>
        <p style="color: #4a5568; font-size: 16px;">Hello {username},</p>
        <p style="color: #4a5568; font-size: 16px;">We detected a new login to your Online Voting System account.</p>
        <p style="color: #4a5568; font-size: 16px;">If this was you, no further action is required.</p>
        <p style="color: #4a5568; font-size: 16px;">If you did not log in recently, please contact our support team immediately to secure your account.</p>
        <p style="color: #4a5568; font-size: 14px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 15px;">
            Regards,<br>
            The Online Voting System Team
        </p>
    </div>
    """
    return send_email(email, subject, html_content=html_content)

def send_candidate_notification(candidate_name, candidate_email, party):
    """Send notification to a newly added candidate"""
    subject = "You've Been Added as a Candidate - Online Voting System"
    results_url = f"{BASE_URL}/results"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
        <h2 style="color: #4a5568; text-align: center;">Candidate Registration Notification</h2>
        <p style="color: #4a5568; font-size: 16px;">Hello {candidate_name},</p>
        <p style="color: #4a5568; font-size: 16px;">You have been added as a candidate representing <strong>{party}</strong> in our Online Voting System.</p>
        <p style="color: #4a5568; font-size: 16px;">Your profile is now visible to voters in the system. If you have any questions or need to update your information, please contact the election administration team.</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{results_url}" style="background-color: #4299e1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Election Results</a>
        </div>
        <p style="color: #4a5568; font-size: 16px;">Good luck with your campaign!</p>
        <p style="color: #4a5568; font-size: 14px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 15px;">
            Regards,<br>
            The Online Voting System Team
        </p>
    </div>
    """
    return send_email(candidate_email, subject, html_content=html_content)