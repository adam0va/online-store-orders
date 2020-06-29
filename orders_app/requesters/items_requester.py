from orders_app.requesters.requester import Requester


class ItemsRequester(Requester):
    #ITEMS_HOST = Requester.HOST + ':8001/'
    ITEMS_HOST = 'https://rsoi-online-store-items.herokuapp.com/'

    def get_item(self, uuid):
        response = self.get_request(self.ITEMS_HOST + str(uuid) + '/')
        if response is None:
            return self.BASE_HTTP_ERROR

        return response, response.status_code
