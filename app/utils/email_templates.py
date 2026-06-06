import os

KAIRA_LOGO_URL = os.getenv("KAIRA_LOGO_URL")
KAIRA_BANNER_URL = os.getenv("KAIRA_BANNER_URL")


def build_otp_email_html(full_name: str, otp: str, title: str, subtitle: str):
    return f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#05001f;font-family:Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#05001f;padding:35px 0;">
<tr>
<td align="center">

<table width="600" cellpadding="0" cellspacing="0"
style="background:#0d0933;border-radius:24px;overflow:hidden;color:#ffffff;">

<tr>
<td background="{KAIRA_BANNER_URL}" style="
background-image:url('{KAIRA_BANNER_URL}');
background-size:cover;
background-position:center;
height:260px;
text-align:center;
vertical-align:bottom;
padding-bottom:25px;
">

<img src="{KAIRA_LOGO_URL}" width="95" alt="Kaira Logo"
style="display:block;margin:0 auto 10px auto;border-radius:50%;">

<h1 style="margin:0;color:#d6b8ff;letter-spacing:8px;font-size:30px;">
KAIRA
</h1>

<p style="margin:8px 0 0;color:#ddd3ff;font-size:13px;">
AI Astrology Interpretation
</p>

</td>
</tr>

<tr>
<td style="padding:38px 42px;background:#100b3a;">

<h2 style="margin:0 0 22px;color:#ffffff;font-size:22px;">
Hello {full_name} ✨
</h2>

<p style="color:#ddd8ff;font-size:15px;line-height:1.7;margin:0 0 28px;">
{subtitle}
</p>

<div style="
background:linear-gradient(135deg,#32136d,#6b2ee8);
padding:28px;
border-radius:18px;
text-align:center;
margin:0 0 28px;
">

<p style="margin:0 0 12px;color:#d8caff;font-size:12px;">
Your OTP Code
</p>

<div style="
font-size:42px;
font-weight:bold;
letter-spacing:10px;
color:#ffffff;
">
{otp}
</div>

</div>

<p style="color:#d8d3ff;font-size:14px;line-height:1.6;">
This OTP will expire soon. Please do not share it with anyone.
</p>

<p style="color:#d8d3ff;font-size:14px;line-height:1.6;margin-top:24px;">
Thank you,<br>
Kaira Team
</p>

</td>
</tr>

<tr>
<td align="center" style="padding:18px;background:#090625;color:#9f94d8;font-size:12px;">
© Kaira. Astrology data interpretation powered by AI.
</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""