from orders_app.requesters.requester import Requester
from orders_app.requesters.authrequester import AuthRequester

class BillingRequester(Requester):
    #BILLING_HOST = Requester.HOST + ':8000/'
    BILLING_HOST = 'https://rsoi-online-store-billing.herokuapp.com/'

    def get_billing(self, uuid, token=None):
        headers = {}
        print(uuid)
        if token:
            headers = AuthRequester()._create_auth_header(token)
        response = self.get_request(self.BILLING_HOST + str(uuid) + '/', headers=headers)
        if response is None:
            return self.BASE_HTTP_ERROR
        #print(response.json())

        return response, response.status_code

    def post_billing(self, data={}, token=None):
        headers = {}
        if token:
            headers = AuthRequester()._create_auth_header(token)
        response = self.post_request(self.BILLING_HOST, data=data, headers=headers)
        if response is None:
            return self.BASE_HTTP_ERROR
        return response, response.status_code

    def delete_billing(self, uuid, token=None):
        headers = {}
        if token:
            headers = AuthRequester()._create_auth_header(token)
        response = self.delete_request(self.BILLING_HOST + str(uuid) + '/', headers=headers)
        if response is None:
            return self.BASE_HTTP_ERROR
        return self.get_data_from_response(response), response.status_code
