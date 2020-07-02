from rest_framework.permissions import BasePermission
from orders_app.requesters.authrequester import AuthRequester
from orders_app.requesters.requester import Requester


class BaseApiRequestError(Exception):
    def __init__(self, message: str = 'BaseApiRequestError was raised'):
        self.message = message

    def __str__(self):
        return self.message

# просматривать информацию обо всех пользователях, удалять может только админ
# просматривать информацию о конкретном пользователе может он сам и админ

class BaseAuthPermission(BasePermission):
    def _get_token_from_request(self, request):
        return Requester().get_token_from_request(request)


class CustomerAdminPermission(BasePermission):
    def has_permission(self, request, view):
        try:
            if request.method == 'GET':
                return True
            r = AuthRequester()
            response, status_code = r.get_user_info(r.get_token_from_request(request))
            auth_json = r.get_data_from_response(response)
            print(auth_json)
            try:
                return int(view.kwargs[view.lookup_url_kwarg]) == auth_json['id'] or auth_json['is_superuser']
            except KeyError:
                return False
        except BaseApiRequestError:
            return False


class IsSuperuser(BaseAuthPermission):
    AUTH_REQUESTER = AuthRequester()

    def has_permission(self, request, view):
        print(2)
        token = self.AUTH_REQUESTER.get_token_from_request(request)
        if token is None:
            return False
        response, response_status_code = self.AUTH_REQUESTER.get_user_info(token)
        response_data = self.AUTH_REQUESTER.get_data_from_response(response)
        try:
            print(response_data['is_superuser'])
            return response_data['is_superuser']
        except KeyError:
            return False


class IsAuthenticated(BaseAuthPermission):
    AUTH_REQUESTER = AuthRequester()

    def has_permission(self, request, view):
        token = self.AUTH_REQUESTER.get_token_from_request(request)
        if token is None:
            return False
        return AuthRequester().is_token_valid(token)[1]


class IsAppTokenCorrect(BaseAuthPermission):
    AUTH_REQUESTER = AuthRequester()

    def has_permission(self, request, view):
        token = self.AUTH_REQUESTER.get_token_from_request(request)
        if token is None:
            return False
        view.app_access_token = token
        return AuthRequester().app_verify_token(token)[1]
