class CrossOriginResourcePolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/media/'):
            response['Cross-Origin-Resource-Policy'] = 'cross-origin'
            response['Access-Control-Allow-Origin'] = 'https://flakyfantasy.com'
        return response