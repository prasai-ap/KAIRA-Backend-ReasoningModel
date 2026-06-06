import os

KAIRA_LOGO_URL = os.getenv("KAIRA_LOGO_URL", "")
KAIRA_BANNER_URL = os.getenv("KAIRA_BANNER_URL", "")


def build_otp_email_html(full_name: str, otp: str, title: str, subtitle: str):
    return f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#05001f;font-family:Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0"
style="
background-color:#05001f;
background-image:url('{KAIRA_BANNER_URL}');
background-size:cover;
background-position:center top;
background-repeat:no-repeat;
padding:80px 20px;
">
<tr>
<td align="center">

<table width="620" cellpadding="0" cellspacing="0"
style="
background:rgba(10,8,45,0.94);
border:1px solid #6b2ee8;
border-radius:28px;
overflow:hidden;
color:#ffffff;
box-shadow:0 0 40px rgba(107,46,232,0.35);
">
<tr>
<td align="center" style="padding:42px 46px 20px;">

<img src="{KAIRA_LOGO_URL}" width="95" alt="Kaira Logo"
style="display:block;margin:0 auto 18px;border-radius:50%;">

<h1 style="
margin:0;
color:#d8c4ff;
letter-spacing:10px;
font-size:34px;
font-weight:700;
">
KAIRA
</h1>

<p style="
margin:10px 0 0;
color:#d8d0ff;
font-size:16px;
">
AI Astrology Interpretation
</p>

</td>
</tr>

<tr>
<td style="padding:34px 46px 20px;">

<h2 style="
margin:0 0 24px;
color:#ffffff;
font-size:26px;
font-weight:700;
">
Hello {full_name} ✨
</h2>

<p style="
color:#ddd8ff;
font-size:17px;
line-height:1.7;
margin:0 0 30px;
">
{subtitle}
</p>

<div style="
background:linear-gradient(135deg,#2d105f,#702df0);
padding:34px 24px;
border-radius:22px;
text-align:center;
margin:0 0 34px;
border:1px solid #8b5cf6;
">

<p style="
margin:0 0 16px;
color:#ded2ff;
font-size:15px;
">
Your OTP Code
</p>

<div style="
font-size:52px;
font-weight:bold;
letter-spacing:16px;
color:#ffffff;
line-height:1;
">
{otp}
</div>

</div>

<p style="
color:#d8d3ff;
font-size:16px;
line-height:1.6;
margin:0 0 28px;
">
This OTP will expire soon. Please do not share it with anyone.
</p>

<p style="
color:#d8d3ff;
font-size:16px;
line-height:1.6;
margin:0;
">
Thank you,<br>
Kaira Team
</p>

</td>
</tr>

<tr>
<td align="center" style="
padding:22px;
border-top:1px solid rgba(139,92,246,0.25);
color:#9f94d8;
font-size:13px;
">
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