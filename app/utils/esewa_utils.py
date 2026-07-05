import base64
import hmac
import hashlib


def generate_esewa_signature(total_amount: int, transaction_uuid: str, product_code: str, secret_key: str):
    message = (
        f"total_amount={total_amount},"
        f"transaction_uuid={transaction_uuid},"
        f"product_code={product_code}"
    )

    signature = hmac.new(
        secret_key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(signature).decode("utf-8")