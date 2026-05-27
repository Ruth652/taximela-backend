import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

FROM_EMAIL = "onboarding@resend.dev"


def send_admin_invite_email(to: str, full_name: str, role: str, reset_link: str) -> None:
    """
    Sends a branded TaxiMela admin invitation email with a password-setup link.
    """

    role_display = {
        "super_admin": "Super Admin",
        "operational_admin": "Operational Admin",
        "business_admin": "Business Admin",
    }.get(role, role.replace("_", " ").title())

    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Welcome to TaxiMela Admin</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f6f9;font-family:'Segoe UI',Arial,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f9;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0"
               style="background-color:#ffffff;border-radius:12px;overflow:hidden;
                      box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background-color:#1a1a2e;padding:36px 40px;text-align:center;">
              <h1 style="margin:0;color:#f5a623;font-size:28px;font-weight:800;
                         letter-spacing:1px;">🚖 TaxiMela</h1>
              <p style="margin:8px 0 0;color:#a0aec0;font-size:13px;letter-spacing:2px;
                        text-transform:uppercase;">Admin Portal</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px 40px 32px;">
              <h2 style="margin:0 0 8px;color:#1a1a2e;font-size:22px;font-weight:700;">
                Welcome, {full_name}!
              </h2>
              <p style="margin:0 0 24px;color:#4a5568;font-size:15px;line-height:1.6;">
                You've been added to the TaxiMela admin team as a
                <strong style="color:#1a1a2e;">{role_display}</strong>.
                To get started, set up your password by clicking the button below.
              </p>

              <!-- Role badge -->
              <table cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                <tr>
                  <td style="background-color:#fff8ec;border:1px solid #f5a623;
                              border-radius:6px;padding:10px 18px;">
                    <span style="color:#b7791f;font-size:13px;font-weight:600;">
                      Role: {role_display}
                    </span>
                  </td>
                </tr>
              </table>

              <!-- CTA Button -->
              <table cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                <tr>
                  <td align="center"
                      style="background-color:#f5a623;border-radius:8px;">
                    <a href="{reset_link}"
                       style="display:inline-block;padding:14px 36px;
                              color:#1a1a2e;font-size:15px;font-weight:700;
                              text-decoration:none;letter-spacing:0.3px;">
                      Set Up My Password →
                    </a>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 8px;color:#718096;font-size:13px;line-height:1.6;">
                This link expires in <strong>24 hours</strong>. If you didn't expect this
                email, you can safely ignore it.
              </p>
              <p style="margin:0;color:#718096;font-size:13px;line-height:1.6;">
                If the button doesn't work, copy and paste this link into your browser:
              </p>
              <p style="margin:8px 0 0;word-break:break-all;">
                <a href="{reset_link}"
                   style="color:#f5a623;font-size:12px;text-decoration:none;">
                  {reset_link}
                </a>
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color:#f7fafc;border-top:1px solid #e2e8f0;
                        padding:24px 40px;text-align:center;">
              <p style="margin:0;color:#a0aec0;font-size:12px;line-height:1.6;">
                © 2026 TaxiMela · Addis Ababa, Ethiopia<br/>
                This is an automated message — please do not reply.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
"""

    params: resend.Emails.SendParams = {
        "from": f"TaxiMela Admin <{FROM_EMAIL}>",
        "to": [to],
        "subject": "You've been added to TaxiMela — Set up your password",
        "html": html_body,
    }
    resend.Emails.send(params)
