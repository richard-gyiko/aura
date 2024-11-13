from zoneinfo import ZoneInfo

from tzlocal import get_localzone


def get_local_timezone() -> ZoneInfo:
    """Get the current system timezone."""

    return ZoneInfo(str(get_localzone()))
