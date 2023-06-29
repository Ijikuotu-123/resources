from flask import request
from flask_restful import Resource
from flask_jwt_extended import( 
 create_access_token,
 create_refresh_token,
 jwt_refresh_token_required,
 get_jwt_identity,
 jwt_required,
 fresh_jwt_required)
from werkzeug.security import save_str_cmp # for comparing strings during authentification

from model.User import UserModel
from schemas.User import UserSchema
from blacklist import BLACKLIST
from libs.maligun import MailGunException
from libs.string import gettext

USER_ALREADY_EXIST = "a use with that username already exists."
CREATED_SUCCESSFULY = "user created successfully."
USER_NOT_FOUND = "user not found."
USER_DELETED ="use deleted."
INVALID_CREDENTIALS = "invalid credentials !"
USER_LOGGED_OUT = "user id<{user_id}> successfully logged out"
NOT_CONFIRMED_ERROR = "you have not confirmed registration, please check your emial {}"
USER_CONFIRMED = " user confirmed"

User_schema = UserSchema()


request.get[form]

class UserRegister(resource):
    @ classmethod
    def post(cls):
        try:
            User_data = User_schema.load(request.get_json())
        #with flask_marshmallow the above line gives a user_object and not data(dictionary) 
        # where we have user_data becomes user. 
            User = User_schema.load(request.get_json())
        except validationerror as err:
            return err. message,400

        if UserModel.find_by_username(user_data['username']): #user_data['username'] becomes user.username 
            return {"Message": USER_ALREADY_EXIST}, 400   # 400 represent bad request. i.e what u want already exist

        user = UserModel(**user_data) # with flask_marshmallow we don't need this as the object has already been created
        user.save_to_db()

        return {"message": CREATED_SUCCESSFULY}, 201 # 201 means it has been created

# marshmallow and reqparse can be used to extract data of a particular type from the incoming json,form data etc


class UserRegister(Resource):
    @classmethod()
    def post(cls):
        user_json = request.get_json()
        user = user_schema.load(user_json)
        
        if UserModel.find_by_username(user.username):
            return {"message" : USER_ALREADY_EXISTS}, 400
            return {"message" : gettext("user_already_exist")}, 400 # do this when u have a lib for your strings
        
        if UserModel.find_by_email(user.email):
            return {"message" : USER_ALREADY_EXISTS}, 400

        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": SUCCESS_REGISTER_MESSAGE}, 201
        except MailGunException as e: # mailgun failed to send the email
            user.delete_from_db()
            return {"message": str(e)}, 500
        except:     # This handles a situation where saving to the db does not work
            traceback.print_exc()
            user.delete_from_db()
            return {"message": FAILED_TO_CREATE}, 500
        

class UserLogin(resource): # flask_marshmallow
    @ classmethod()
    def post (cls):
        try:
            User_data = User_schema.load(request.get_json())  # object model is produced
        
        except validationerror as err:
            return err. message,400
        # lines 33 and 34 are for authentication
        user = UserModel.find_by_username(user_data.username) # check for the object in db
        
        if user and user.password and safe_str_cmp(user.password,user_data.password): # with flask_marsh, user_data['password'] == user_data.password
            # lines 37 and 38 are for identity
           # this checks if they have clicked on the link sent to their mail
            confirmation = user.most_recent_confirmation # this brings out the most recent confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity = user.id,expires_delta=(minutes==30), fresh = True ) # same as identity function (access_token=jwt)
                refresh_token = create_refresh_token(user.id)
                return ({"access_token": access_token, "refresh_token": refresh_token}), 200
            return {'message':NOT_CONFIRMED_ERROR.format(user.email)}, 400  # in place of user.email will use user.username but later remove it
        return {"Message": INVALID_CREDENTIALS},401


class UserLogin(resource):  # marshallow
    @ classmethod()
    def post (cls):
        try:
            User_data = User_schema.load(request.get_json())  # this changes the json into a dictionary with marshmallow
           # or 
            user_json = request.get_json()
            user_data = user_schema.load(user_json)
                
        except validationerror as err:
            return err. message,400
        # lines 33 and 34 are for authentication
        user = UserModel.find_by_username(user_data['username']) # with flask_marsh, user_data['username'] == user_data.username
        
        if user and user.password and safe_str_cmp(user.password,user_data['password']): # with flask_marsh, user_data['password'] == user_data.password
            # lines 37 and 38 are for identity
           # this checks if they have clicked on the link sent to their mail
            confirmation = user.most_recent_confirmation # this brings out the most recent confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity = user.id,expires_delta=(minutes==30), fresh = True ) # same as identity function (access_token=jwt)
                refresh_token = create_refresh_token(user.id)
                return ({"access_token": access_token, "refresh_token": refresh_token}), 200
            return {'message':NOT_CONFIRMED_ERROR.format(user.email)}, 400  # in place of user.email will use user.username but later remove it
        return {"Message": INVALID_CREDENTIALS},401




class User(Resource):
    # this resource can be useful when testing our Flask app. we may not want to expose it to public users, but for the
    # for the sake of demonstration in this course, it can be useful when we are manipulating data regarding users.
    @ classmethod
    def get (cls, user_id: int):
        user = UserModel.find_user_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND},404
        return user_schema.dump(user), 200

    @ classmethod()
    def delete (cls, user_id:int):
        user = UserModel.find_user_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND},404 
        user.delete_frm_db()
        return {"message": USER_DELETED}, 200 
        
class UserLogout(Resource):   # uses blacklist
    @classmethod   # we are blacklisting the jwt id and not the user_id. if the user_id, it means they won't be able to access anything if they login
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"] # jti is a unique identifier for JWT
        user_id =get_jwt_identity()   # u may not add this since i would not want to display the person's id
        BLACKLIST.add(jti)   # BLACKLIST is a set so we can add things to it
        return {"message": USER_LOGGED_OUT.format(user_id)}, 200

class TokenRefresh(Resource):  # helps to generate  a non-fresh access token when the one we are expires
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity =current_user, fresh = False)
        return {"access_token":new_token},200

class SetPassword(Resource):
    @ classmethod
    @ fresh_jwt_required
    def post(cls):
        user_json = request.get_json()
        user_data = user_schema.load(user_json)   # username and new password
        user = UserModel.find_by_username(user_data.username)
        if not user:
            return {'message':gettext('user_not_found')}, 400

        user.password = user_data.password
        user.save_to_db()
        return {'message': gettext('user_password_updated')}, 201




