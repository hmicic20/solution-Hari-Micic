from slowapi import Limiter
from slowapi.util import get_remote_address

from tickethub.config import settings

# Osnovni limiter po IP adresi klijenta
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_default],
)
