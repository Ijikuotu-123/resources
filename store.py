from flask_restful import Resource
from model.store import StoreModel
from schemas.store import StoreSchema

store_schema = StoreSchema()
store_list_schema = StoreSchema(many = True)

STORE_NOT_FOUND = "store not found"
STORE_NAME_ALREADY_EXISTS= "a store with the name '{}' already exists"


class Store(Resource):    # we wont do a put because changing a store's name changes everything about it.
    def get(self,name:str):
        store = StoreModNAME_ALREADY_EXISTSel.find_by_name(name)
        if store:
            #return store.json(),200
            return store_schema.dump(store), 200   # flask_marshmallow
        return {"message":ITEM_NOT_FOUND}, 404

    def post (self,name: str):
        if StoreModel.find_by_name(name):
            return {"message":STORE_NAME_ALREADY_EXISTS. format(name)},400
        store = StoreModel(name=name)   # creating the object. note store has only name as it property so we wont request json
# store above will channge with flask_marshmallow because we don't have  __init___ again.
        store = StoreModel(name=name)
        try:
            store.save_to_db()
        except:
            return {"message":"an error occurred whlie creating the store"},500 # 500 means we are not sure what the error was
            # then it is the fault of the database, internal server error
        #return store.json(), 201
        return store_schema.dump(store), 201

    def delete (self,name: str):
        store = StoreModel.find_by_name(name)
        if store:                          # if the store doesn't exist it doesn't matter because we want to delete it
            store.delete_from_db()
        return {"message":"store deleted"}
        
            
class StoreList(Resource):
    def get (self):
        #return {'stores':[store_schema.dump(store) for store in StoreModel.query.all()]}
        return {'stores': store_list_schema.dump(StoreModel.find_all())}
