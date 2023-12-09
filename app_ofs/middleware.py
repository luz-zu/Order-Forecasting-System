
from django.utils.deprecation import MiddlewareMixin

class CurrentUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        global current_user_id
        current_user_id = request.user.id
