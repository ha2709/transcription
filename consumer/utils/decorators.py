import functools
import time


# Rate limit decorator
def rate_limit(max_requests, time_window):
    """
    Rate limiting decorator to limit the number of requests per IP address within a time window.

    :param max_requests: Maximum number of allowed requests.
    :param time_window: Time window in seconds.
    """

    def decorator(func):
        requests_cache = {}

        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Get client IP address
            ip = request.META.get("REMOTE_ADDR")
            current_time = time.time()
            request_log = requests_cache.get(ip, [])

            # Remove outdated requests
            request_log = [
                timestamp
                for timestamp in request_log
                if current_time - timestamp < time_window
            ]

            # if len(request_log) >= max_requests:
            #     return Response(
            #         {"error": "Rate limit exceeded. Try again later."},
            #         status=status.HTTP_429_TOO_MANY_REQUESTS,
            #     )

            # Log the current request
            request_log.append(current_time)
            requests_cache[ip] = request_log

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


# Caching decorator
def cache(func):
    cache_data = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache_data:
            cache_data[key] = func(*args, **kwargs)
        return cache_data[key]

    return wrapper


# Logging decorator
def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(
            f"Function {func.__name__} called with args: {args}, kwargs: {kwargs} - took {end_time - start_time:.4f}s"
        )
        return result

    return wrapper


# Access control decorator
def require_permission(permission):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not getattr(args[0], "has_permission", False):
                raise PermissionError("Permission denied.")
            return func(*args, **kwargs)

        return wrapper

    return decorator
