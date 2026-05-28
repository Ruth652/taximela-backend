import os
import requests
from dotenv import load_dotenv

load_dotenv()

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
FROM_EMAIL = "taximela.app@gmail.com"
FROM_NAME = "Taximela Admin"


def send_admin_invite_email(to: str, full_name: str, role: str, reset_link: str) -> None:
    """
    Sends a branded Taximela admin invitation email with a password-setup link via Brevo.
    """

    role_display = {
        "super_admin": "Super Admin",
        "operational_admin": "Operational Admin",
        "business_admin": "Business Admin",
    }.get(role, role.replace("_", " ").title())

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Taximela Admin Invite</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=Space+Mono&display=swap" rel="stylesheet"/>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: #0E1117;
      font-family: 'DM Sans', Arial, sans-serif;
      color: #E8EDF5;
      padding: 40px 16px;
    }}
    .wrapper {{ max-width: 520px; margin: 0 auto; }}
    .card {{
      background-color: #161B24;
      border: 1px solid #252E42;
      border-radius: 16px;
      overflow: hidden;
    }}
    .header {{ padding: 36px 40px 28px; border-bottom: 1px solid #252E42; }}
    .brand-row {{ display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }}
    .brand-dot {{
      width: 10px; height: 10px;
      background-color: #2DD4A0;
      border-radius: 50%;
      display: inline-block;
      flex-shrink: 0;
    }}
    .brand-name {{
      font-family: 'DM Sans', Arial, sans-serif;
      font-weight: 600; font-size: 22px;
      color: #E8EDF5; letter-spacing: -0.3px;
    }}
    .brand-tagline {{
      font-family: 'DM Sans', Arial, sans-serif;
      font-weight: 700; font-size: 9px;
      letter-spacing: 2.5px; text-transform: uppercase;
      color: #8A92A3; margin-left: 18px;
    }}
    .body {{ padding: 36px 40px; }}
    .greeting {{
      font-family: 'DM Sans', Arial, sans-serif;
      font-weight: 600; font-size: 20px;
      color: #E8EDF5; margin-bottom: 16px;
    }}
    .role-badge {{
      display: inline-block;
      background-color: rgba(45, 212, 160, 0.12);
      border: 1px solid rgba(45, 212, 160, 0.35);
      border-radius: 6px; padding: 5px 12px;
      font-family: 'Space Mono', monospace;
      font-size: 12px; color: #2DD4A0; margin-bottom: 20px;
    }}
    .message {{
      font-family: 'DM Sans', Arial, sans-serif;
      font-weight: 400; font-size: 15px;
      color: #8A92A3; line-height: 1.7; margin-bottom: 32px;
    }}
    .divider {{ border: none; border-top: 1px solid #252E42; margin: 0 0 28px; }}
    .cta-btn {{
      display: inline-block;
      background-color: #2DD4A0; color: #0E1117;
      font-family: 'DM Sans', Arial, sans-serif;
      font-weight: 600; font-size: 15px;
      text-decoration: none; padding: 14px 36px;
      border-radius: 10px; letter-spacing: 0.2px; margin-bottom: 28px;
    }}
    .expiry-note {{
      font-family: 'DM Sans', Arial, sans-serif;
      font-size: 13px; color: #8A92A3; line-height: 1.6; margin-bottom: 8px;
    }}
    .fallback-label {{
      font-family: 'DM Sans', Arial, sans-serif;
      font-size: 12px; color: #8A92A3; margin-bottom: 6px;
    }}
    .fallback-link {{
      font-family: 'Space Mono', monospace;
      font-size: 11px; color: #2DD4A0;
      word-break: break-all; text-decoration: none;
    }}
    .footer {{ padding: 20px 40px; border-top: 1px solid #252E42; text-align: center; }}
    .footer p {{
      font-family: 'DM Sans', Arial, sans-serif;
      font-size: 12px; color: #8A92A3; line-height: 1.6;
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="card">
      <div class="header">
        <div class="brand-row">
          <span class="brand-dot"></span>
          <span class="brand-name">Taximela.</span>
        </div>
        <div class="brand-tagline">Management System</div>
      </div>
      <div class="body">
        <p class="greeting">Hello, {full_name}</p>
        <div class="role-badge">{role_display}</div>
        <hr class="divider"/>
        <p class="message">
          You've been added as a <strong style="color:#E8EDF5;">{role_display}</strong> admin.<br/>
          Click the button below to set your password and access the dashboard.
        </p>
        <a href="{reset_link}" class="cta-btn">Set Your Password</a>
        <hr class="divider"/>
        <p class="expiry-note">This link expires in <strong style="color:#E8EDF5;">24 hours</strong>.</p>
        <p class="expiry-note" style="margin-bottom:20px;">If you didn't expect this email, you can safely ignore it.</p>
        <p class="fallback-label">Or copy this link into your browser:</p>
        <a href="{reset_link}" class="fallback-link">{reset_link}</a>
      </div>
      <div class="footer">
        <p>&copy; Taximela &nbsp;&middot;&nbsp; Authorized Personnel Only</p>
      </div>
    </div>
  </div>
</body>
</html>"""

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "api-key": BREVO_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "sender": {"name": FROM_NAME, "email": FROM_EMAIL},
            "to": [{"email": to, "name": full_name}],
            "subject": "You've been added to Taximela — Set up your password",
            "htmlContent": html_body,
        },
    )

    if response.status_code not in (200, 201):
        raise Exception(f"Brevo email failed: {response.status_code} {response.text}")
