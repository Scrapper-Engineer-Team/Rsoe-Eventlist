import re


class AccountNotFoundException(Exception):
    def __str__(self):
        return "Account not found"


class PrivateAccountException(Exception):
    def __str__(self):
        return "Account is private"


class NoProxiesAvailableException(Exception):
    def __str__(self):
        return "No proxies available"


class ChannelNotExists(Exception):
    def __str__(self):
        return "ChannelNotExists"


class ErrorRequestException(Exception):
    pass


class RateLimitExceeded(Exception):
    pass


class ResponseException(Exception):
    def __init__(self, message="internal server error", status=500):
        super(ResponseException, self).__init__(message)
        self.message = message
        self.status = status


class BadRequestResponseException(ResponseException):
    def __init__(self, message="bad request"):
        super(BadRequestResponseException, self).__init__(message, status=400)


class MessageException:
    TOO_MANY_REQUEST = ["Too Many Requests", "Too Many Redirects"]
    CONNECTION_TIMEOUT = [
        "ReadTimeout",
        "Read Timed out",
        "ConnectTimeout",
        "Connection Timed out",
        "Connect Timeout",
        "Timed Out",
        "Cannot connect to proxy",
    ]
    CONNECTION_ERROR = [
        "Failed to establish a new connection",
        "Connection reset by peer",
    ]
    PROXY_ERROR = ["Cannot connect to proxy"]
    JSON_DECODE_ERROR = ["JSONDecodeError"]

    def too_many_requests(self):
        pattern = r"|".join(self.TOO_MANY_REQUEST)
        return re.compile(pattern=pattern, flags=re.I)

    def connection_timeout(self):
        pattern = r"|".join(self.CONNECTION_TIMEOUT)
        return re.compile(pattern=pattern, flags=re.I)

    def connection_error(self):
        pattern = r"|".join(self.CONNECTION_ERROR)
        return re.compile(pattern=pattern, flags=re.I)

    def proxy_error(self):
        pattern = r"|".join(self.PROXY_ERROR)
        return re.compile(pattern=pattern, flags=re.I)

    def json_decode_error(self):
        pattern = r"|".join(self.JSON_DECODE_ERROR)
        return re.compile(pattern=pattern, flags=re.I)


class OutputDriverNotRecognizeException(Exception):
    def __str__(self):
        return "Destination not recognized"


class TiktokBlockedByCaptchaException(Exception):
    def __str__(self):
        return "Blocked by captcha"


class TiktokCookiesExpiredException(Exception):
    def __str__(self):
        return "Cookies expired"


class TiktokTryAgainException(Exception):
    def __str__(self):
        return "Try again later"


class TiktokUnknownException(Exception):
    def __str__(self):
        return "Unknown error"
