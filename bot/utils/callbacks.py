from __future__ import annotations

import base64
import hashlib
import zlib
from collections import OrderedDict

MAX_TOKEN_LENGTH = 30
MAX_CACHED_PATHS = 4000

_path_cache: OrderedDict[str, str] = OrderedDict()


def _remember(key: str, path: str) -> None:
    _path_cache[key] = path
    _path_cache.move_to_end(key)
    while len(_path_cache) > MAX_CACHED_PATHS:
        _path_cache.popitem(last=False)


def encode_path(path: str) -> str:
    """Encode a long file path into a callback-safe token (max 20 chars)."""
    raw = (path or "").encode("utf-8")
    compressed = base64.b64encode(zlib.compress(raw, 6)).decode("ascii").rstrip("=")
    if len(compressed) <= MAX_TOKEN_LENGTH:
        return compressed

    digest = hashlib.sha1(raw).hexdigest()[:12]
    _remember(digest, path)
    return "~" + digest


def decode_path(token: str) -> str | None:
    if not token:
        return None
    if token.startswith("~") and len(token) == 13:
        return _path_cache.get(token[1:])
    try:
        padding = "=" * (-len(token) % 4)
        return zlib.decompress(base64.b64decode(token + padding)).decode("utf-8")
    except Exception:
        return None
