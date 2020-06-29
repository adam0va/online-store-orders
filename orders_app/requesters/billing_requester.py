from orders_app.requesters.requester import Requester

class BillingRequester(Requester):
    #BILLING_HOST = Requester.HOST + ':8000/'
    BILLING_HOST = 'https://rsoi-online-store-items.herokuapp.com/'

    def get_billing(self, uuid):
        response = self.get_request(self.BILLING_HOST + str(uuid) + '/')
        if response is None:
            return self.BASE_HTTP_ERROR

        return response, response.status_code

    def patch_billing(self, request, uuid):
        pass

    def delete_billing(self, uuid):
        response = self.delete_request(self.BILLING_HOST + str(uuid) + '/')
        if response is None:
            return self.BASE_HTTP_ERROR
        return self.get_data_from_response(response), response.status_code
