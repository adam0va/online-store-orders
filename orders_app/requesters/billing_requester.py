from orders_app.requesters.requester import Requester

class BillingRequester(Requester):
    BILLING_HOST = Requester.HOST + ':8000/'
    #BILLING_HOST = 'https://rsoi-online-store-billing.herokuapp.com/'

    def get_billing(self, uuid):
        response = self.get_request(self.BILLING_HOST + str(uuid) + '/')
        if response is None:
            return self.BASE_HTTP_ERROR

        return response, response.status_code

    def post_billing(self, data={}):
        response = self.post_request(self.BILLING_HOST, data=data)
        if response is None:
            return self.BASE_HTTP_ERROR
        return response, response.status_code

    def delete_billing(self, uuid):
        response = self.delete_request(self.BILLING_HOST + str(uuid) + '/')
        if response is None:
            return self.BASE_HTTP_ERROR
        return self.get_data_from_response(response), response.status_code
