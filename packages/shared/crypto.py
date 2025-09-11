import base64
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

# Public key shared with licensing
PUBLIC_KEY_B64 = "5ZyKDtcNYw4keTd5Oq8IWN9sEx0sTy2scgihTK7tBqc="
VERIFY_KEY = VerifyKey(base64.b64decode(PUBLIC_KEY_B64))


def verify_signature(data: bytes, signature_b64: str) -> None:
    """Verify *data* against *signature_b64*.

    Raises ValueError if signature invalid.
    """
    try:
        VERIFY_KEY.verify(data, base64.b64decode(signature_b64))
    except BadSignatureError as exc:  # pragma: no cover - explicit
        raise ValueError("Invalid signature") from exc
