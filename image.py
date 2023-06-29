from flask_restful import Resource
from flask_upload import UploadNotAllowed
from flask import request, send_file
# send_file allows us to send a binary file like an image instead of json
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback # to print out error messages
import os  # to delete images

from libs import image_helper
from libs.strings import gettext
from schemas.image import ImageSchema

imageschema = ImageSchema()

""" User uploading images"""
class ImageUpload(Resource):
    @ jwt_required
    def post(self):
        """ 
        use to upload an image file
        it uses jwt to retrieve user information and then saves the image to the user's folder.
        if there's a filename conflict,it appends a number at the end
          """
        data =imageschema.load(request.files)  # {'image' :filestorage}
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"    # static/images/user_1
        
        try:
            image_path =image_helper.save_image(data["images"],folder = folder)
            basename = image_helper.get_basename(image_path)
            return {"message": gettext("image_upload").format(basename)}, 201
        except UploadNotAllowed:
            extension = image_helper.get_basename(data["images"])
            return {"message":gettext ("image_illegal_extension").format(extension)},400


class Image(Resource):
    @ jwt_required
    def get(self, filename: str):
        # Returns the requested image if it exists. looks up into the logged in user's folder#
        user_id = get_jwt_identity()
        folder = f"user{user_id}"
        if not image_helper.is_filename_safe(filename):
            return {"mesage": gettext("image_illegal_file_name").format(filename)}, 400
        
        try:
            return send_file(image_helper.get_path(filename, folder=folder))
        except FileNotFoundError: 
            return {"message": gettext("image_not_found").format(filename)}, 400

    @ jwt_required
    def delete(self, filename: str):
        user_id = get_jwt_identity()
        folder = f"user{user_id}"
        if not image_helper.is_filename_safe(filename):
            return {"mesage": gettext("image_illegal_file_name").format(filename)}, 400

        try:
            os.remove(image_helper.get_path(filename, folder=folder))
            return {"mesage": gettext("image_deleted").format(filename)}, 200
        except FileNotFoundError:
            return {"message": gettext("image_not_found").format(filename)}, 400
        except:
            traceback.print_exc()
            return {"message": gettext("image_delete_failed")},500
            

class AvaterUpload(Resource):
    # This endpoint is used to upload user avater(profile pics). 
    # All avaters are named after the user's ID. something like this user_{id}.{ext}
    #  uploadig a new one overrides the old one, thus a put request #
    @ jwt_required
    def put(self): # it is a put because it will allow us to post and at the same time edit
        data = imageschema.load(request.files)
        filename = f"user_{get_jwt_identity()}"
        folder = "avaters"
        avater_path = image_helper.find_image_any_format(filename, folder)
        if avater_path:
            try:
                os.remove(avater_path)
            except:
                return {"message":gettext("avater_delete_failed")}, 500
        try:
            ext = image_helper.get_extension(data['image'].filename)  
            # data['image'] is a file storage object that has filename as a property
            avater = filename + ext
            avater_path = image_helper.save_image(
                data['image'], folder = folder, name = avater
            )
            basename = image_helper.get_basename(avater_path)
            return {"message": gettext("avater_uploaded").format(basename)}, 200
        except UploadNotAllowed:
            extension =image_helper.get_extension(data['image'])
            return {"message":gettext("image_illegal_extension").format(extension)},400
class Avater(Resource):
    @ classmethod
    def get (cls, user_id:int):
        folder= "avaters"
        filename = f"user_{user_id}"
        avater_path = image_helper.find_image_any_format(filename, folder)
        if avater:
            return send_file(avater)
        return {"message": gettext("avater_not_found")},404
   

