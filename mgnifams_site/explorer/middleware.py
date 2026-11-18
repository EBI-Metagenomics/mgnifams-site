def no_cache_by_default(get_response):
    """Responses without their own Cache-Control must be revalidated, so a shared front cache never
    serves an old page (one rendered while Skylign failed, or before a DB swap) to every visitor."""

    def middleware(request):
        response = get_response(request)
        if 'Cache-Control' not in response:
            response['Cache-Control'] = 'no-cache'
        return response

    return middleware
