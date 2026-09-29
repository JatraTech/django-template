class OverrideContentTypeMiddleware:
    """
    Middleware that overrides the Content-Type to `application/json`
    if it's not present in the request headers.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if Content-Type is missing or empty
        if not request.content_type:
            request.META["CONTENT_TYPE"] = "application/json"  # Set Content-Type as application/json
        response = self.get_response(request)
        return response
