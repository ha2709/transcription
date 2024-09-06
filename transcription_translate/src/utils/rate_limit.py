import time
from functools import wraps
from fastapi import HTTPException, Request, status


def rate_limited(max_calls: int, time_frame: int):
    """
    :param max_calls: Maximum number of calls allowed in the specified time frame.
    :param time_frame: The time frame (in seconds) for which the limit applies.
    :return: Decorator function.
    """

    def decorator(func):
        calls = []

        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            now = time.time()
            calls_in_time_frame = [call for call in calls if call > now - time_frame]
            if len(calls_in_time_frame) >= max_calls:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded.",
                )
            calls.append(now)
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator