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
def build_invoice_email_template(user, payment, subscription):
    full_name = escape(user.full_name or "User")
    invoice_number = payment.invoice_number or f"INV-{payment.transaction_uuid}"

    subject = f"Kaira Payment Invoice - {invoice_number}"

    html_body = f"""
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
Payment Successful ✨
</h2>

<p style="
color:#ddd8ff;
font-size:17px;
line-height:1.7;
margin:0 0 30px;
">
Hello {full_name}, thank you for subscribing to Kaira Premium. Your unlimited chat package is now active.
</p>

<div style="
background:linear-gradient(135deg,#2d105f,#702df0);
padding:28px 24px;
border-radius:22px;
margin:0 0 34px;
border:1px solid #8b5cf6;
">

<table width="100%" cellpadding="8" cellspacing="0" style="color:#ffffff;font-size:15px;">
<tr>
<td><strong>Invoice Number</strong></td>
<td align="right">{invoice_number}</td>
</tr>
<tr>
<td><strong>Package</strong></td>
<td align="right">{payment.package_name}</td>
</tr>
<tr>
<td><strong>Amount Paid</strong></td>
<td align="right">NPR {payment.amount}</td>
</tr>
<tr>
<td><strong>Payment Method</strong></td>
<td align="right">eSewa</td>
</tr>
<tr>
<td><strong>Transaction UUID</strong></td>
<td align="right">{payment.transaction_uuid}</td>
</tr>
<tr>
<td><strong>Transaction Code</strong></td>
<td align="right">{payment.transaction_code or "N/A"}</td>
</tr>
<tr>
<td><strong>Subscription Start</strong></td>
<td align="right">{subscription.start_date.strftime("%Y-%m-%d")}</td>
</tr>
<tr>
<td><strong>Subscription End</strong></td>
<td align="right">{subscription.end_date.strftime("%Y-%m-%d")}</td>
</tr>
</table>

</div>

<p style="
color:#d8d3ff;
font-size:16px;
line-height:1.6;
margin:0 0 28px;
">
You can now continue using unlimited Kaira chat until your subscription expiry date.
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

    text_body = f"""
Hello {user.full_name},

Thank you for subscribing to Kaira Premium.

Invoice Number: {invoice_number}
Package: {payment.package_name}
Amount Paid: NPR {payment.amount}
Payment Method: eSewa
Transaction UUID: {payment.transaction_uuid}
Transaction Code: {payment.transaction_code or "N/A"}
Subscription Start: {subscription.start_date.strftime("%Y-%m-%d")}
Subscription End: {subscription.end_date.strftime("%Y-%m-%d")}

Your unlimited Kaira chat package is now active.

Regards,
Kaira Team
"""

    return subject, html_body, text_body

def build_subscription_expiry_email_template(user, subscription):
    full_name = escape(user.full_name or "User")

    subject = "Your Kaira Premium package expires tomorrow"

    html_body = f"""
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
Package Expiring Soon ⏳
</h2>

<p style="
color:#ddd8ff;
font-size:17px;
line-height:1.7;
margin:0 0 30px;
">
Hello {full_name}, your Kaira Premium package will expire tomorrow.
</p>

<div style="
background:linear-gradient(135deg,#2d105f,#702df0);
padding:28px 24px;
border-radius:22px;
margin:0 0 34px;
border:1px solid #8b5cf6;
">

<table width="100%" cellpadding="8" cellspacing="0" style="color:#ffffff;font-size:15px;">
<tr>
<td><strong>Package</strong></td>
<td align="right">{subscription.plan_name}</td>
</tr>
<tr>
<td><strong>Expiry Date</strong></td>
<td align="right">{subscription.end_date.strftime("%Y-%m-%d")}</td>
</tr>
</table>

</div>

<p style="
color:#d8d3ff;
font-size:16px;
line-height:1.6;
margin:0 0 28px;
">
To continue using unlimited Kaira chat without interruption, please renew your subscription before it expires.
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

    text_body = f"""
Hello {user.full_name},

Your Kaira Premium package will expire tomorrow.

Package: {subscription.plan_name}
Expiry Date: {subscription.end_date.strftime("%Y-%m-%d")}

Please renew your subscription before it expires to continue using unlimited Kaira chat.

Regards,
Kaira Team
"""

    return subject, html_body, text_body