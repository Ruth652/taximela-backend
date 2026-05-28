from dotenv import load_dotenv
load_dotenv()

from infrastructure.email_service import send_admin_invite_email

send_admin_invite_email(
    to="haileasaye51@gmail.com",
    full_name="Haile",
    role="operational_admin",
    reset_link="https://example.com/reset?token=test123"
)

print("✅ Email sent! Check your inbox.")
