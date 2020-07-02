from orders_app.requesters.requester import Requester

# просматривать информацию обо всех заказах, удалять может только админ
# просматривать информацию о конкретном заказе может хозян заказа и админ
# добавлять заказ может только приложение

class AuthRequester(Requester):
    #AUTH_HOST = Requester.HOST + ':8004/'
    AUTH_HOST = 'https://rsoi-online-store-auth.herokuapp.com/'

    def _create_auth_header(self, token: str):
        #token_type = 'Bearer' if len(token) < 40 else 'Token'
        token_type = 'Bearer'
        return {'Authorization': f'{token_type} {token}'}

    def get_user_info(self, token):
        auth_header = self._create_auth_header(token)
        response = self.get_request(self.AUTH_HOST + 'user_info/', headers=auth_header)
        if response is None:
            return self.BASE_HTTP_ERROR
        return response, response.status_code

    def register(self, username, password):
        data = {'username': username, 'password': password}
        response = self.post_request(self.AUTH_HOST + 'register/', data=data)
        if response is None:
            return self.BASE_HTTP_ERROR
        return response, response.status_code

    def is_superuser(self, token: str):
        response, status_code = self.get_user_info(token)
        return response['is_superuser']

    def app_get_token(self, app_id: str, app_secret: str):
        data = {
            'id': app_id,
            'secret': app_secret,
        }
        response = self.post_request(url=self.AUTH_HOST + 'api/app-token-auth/', data=data)
        if response is None:
            return self.BASE_HTTP_ERROR
        return response, response.status_code

    def app_verify_token(self, token: str):
        data = {
            'token': token,
        }
        response = self.post_request(url=self.AUTH_HOST + 'api/app-token-verify/', data=data)
        return response, response.status_code

    def app_refresh_token(self, token: str):
        data = {
            'refresh': token,
        }
        response = self.post_request(url=self.AUTH_HOST + 'api/app-token-refresh/', data=data)

        r_json = self.get_data_from_response(response)
        new_token = r_json['access']
        return new_token

    def is_token_valid(self, token: str):
        response = self.post_request(self.AUTH_HOST + 'api/api-token-verify/', data={'token': token})
        if response.status_code is None:
            return Requester().BASE_HTTP_ERROR
        return response, response.status_code
