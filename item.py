from flask import Resources, request
from flask_jwt_extended import jwt_required, fresh_jwt_required,get_jwt_claims
from marshmallow import validationError
from model.item import ItemModel
from schema.item import itemSchema

NAME_ALREADY_EXISTS ="an item with the name {} already exists"
ERROR_INSERTING = "error occurred while inserting item"
ITEM_NOT_FOUND ="item not found"
ITEM_DELETED ="item deleted"

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):
    @classmethod
    @ jwt_required
    def get (cls, name:str):
        item = cls.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @fresh_jwt_required    # this means the user must login(i.e provide his credentials again )
    def post(cls,name:str):
        if cls.find_item_by_name(name):
            return {"Message": NAME_ALREADY_EXISTS.format(name)},400
    
        item_json = request.get_json()
        item_json['name'] = name  # we have to do this because the json does not contain the name but things like price 
   
        try:
            item = item_schema.load(item_json)
        except ValidationError as err:
            return err.message,400
    
        try:
            item.save_to_db()
        except:
            return {"message": ERROR_INSERTING},500
        return item_schema.dump(item),201


    @classmethod    
    @JWT_required  # ordinary JWT will be @JWT_required() but with jwt-extended it will be jwt_required
    def delete (cls, name:str):
        claims =  get_jwt_claims()     # use to make reference to the claim
        if not claims ['is_admin']:
            return {'message': 'Admin privilege reqired'}, 400
        
        item = cls.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message":ITEM_DELETED},200

        return {"message": ITEM_NOT_FOUND},404

    @classmethod()
    def put(cls,name:str):
        item_json = request.get_json()
        item = cls.find_by_name(name)

        if item:
            item.price = item_json['price']
        else:
            item_json['name'] = name

        try:
            item = item_schema.load(item_json)
        except ValidationError as err:
            return err.message,400

        item.save_to_db
        return item_schema.dump(item),200


class ItemList(Resource):
    @classmethod()
    def get(cls):
        #return {"message": [x.json for x in ItemModel.find_all()]}
        #return {"message": [item_schema.dump(item) for x in ItemModel.find_all()]} # with flask marshmallow
        return {"message": item_list_schema.dump(ItemModel.find_all())} # with flask marshmallow

    








