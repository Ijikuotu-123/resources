import traceback

from flask import make_response, render_template 
from flask_restful import Resource

from libs.mailgun import MailGunException
from resources.user import USER_NOT_FOUND   # take note
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema

NOT_FOUND ="confirmation refrence not found"
EXPIRED = "the link has expired"
ALREADY_CONFIRMED = "registration has already been confirmed"


class Confirmation(resoure):
    @classmethod    # main function is to return confirmation html page if the confirmation is just being confirmed
    def get(cls,confirmation_id: str):
        Confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": NOT_FOUND}, 404
        if confirmation.expired:
            return {"message": EXPIRED}, 400
        if confirmation.confirmed:
            return {"message": ALREADY_CONFIRMED},400

        confirmation.confirmed = True
        confirmation.save_to_db()
        headers ={"Content-Type":"text/html"}
        return make_response(
            render_template("confirmation_page.html", email =confirmation.user.email),
            200,
            headers
        )



class ConfirmationByUser(resource):
    @classmethod
    def get(cls):   # returns confirmations from a given user. use for testing
        pass
    

    @classmethod
    def post(cls, user_id:int):  # resend confirmation mail
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": ALREADY_CONFIRMED},400
                confirmation.force_to_expire()
            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db
            user.send_confiramtion_email()
            return {"message" : RESEND_SUCCESSFUL},201
        except MailGunException as e:
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return{"message": RESEND_FAILED},500



