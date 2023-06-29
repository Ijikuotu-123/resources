from collections import Counter
from flask import request
from flask_restful import Resource

from libs.strings import gettext
from models.items import ItemInModel
from models.order import OrderModel,ItemInModel
from schemas.order import OrderSchema

order_schema = OrderSchema
multipe_order_schema = OrderSchema(many=True)


class Order(Resource):
    @classmethod
    def get(cls):
        return multiple_order_schema.dump(OrderModel.find_all()), 200

    @classmethod
    def post(cls):
        ### expect a token and a list of items ids from the request body.
       ### construct an order and talk to Strip API 

        data = request.get_json()  # token + list of items ids [1,2,3,5,5,5]
        items = []  # this should contain items from ItemInModel and not ItemModel
        items_ids_quantities = Counter(data["items_ids"])
        # Counter helps to count each element while the most_common() helps to match each element against its count
        # iterate over the items ids and and retrieve the items from the database
        # items_ids_quantities.most_common gives a list of tuple i.e [(5,3),(3,1),(2,1),(1,1)]
        # in place of below i can do:
        # items_ids_quantities = Counter(data["items_ids"]).most_common -> this return a list of tuple
        for _id, count in items_ids_quantities.most_common(): # [(5,3),(3,1),(2,1),(1,1)]
            item = ItemModel.find_by_id(_id)
            if not item:
                return {"message": gettext("order_item_by_id_not_found")}, 404
            items.append(ItemInModel(item_id = _id, quantity = count))
            order = OrderModel(items=items,status='pending')
            order.save_to_db # this does not submit to stripe
            # here we haven't have stripe to charge. when we send to stripe it either fail or complete
            order.set_status("failed")
            order.charge_with_stripe(data["token"])
            order.set_status("complete")
            return order_schema.dump(order)
         






