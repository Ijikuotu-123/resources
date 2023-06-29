from flask import g
from flask_restful import Resource    # for creating resource
from oa import github                 # import the client created in oa.py
from flask_jwt_extended import create_access_token,create_refresh_token
from model.user import UserModel
# the first step is to tell github that we want to authorize the user and we do that by sending the user to github 
# authorization page alog side  our details.github then send the user to login page or select your account if already
#  logged in. fortunately, the github client we have created can achieve this by the authorization method

class GithubLogin(Resource):  # this should be tested in a browser
    @ classmethod
    def get(cls):  # the authorize function sends the user to github page for authentication with our details(the callback, where to return the user after authorization)
        return github.authorize(callback="http://localhost:5000/login/github/authorized") # this can be rewritten as:
        return github.authorize(url_for("github.authorize",_external=True))


class GithubAuthorize(Resource):
    @classmethod
    def get (cls):
        resp = github.authorized_response()  # authorized respose give us only the access token
        g.access_token = resp['access_token']   # putting our access token inside g
        github_user =github.get('user', token= g.access_token)  # this gets the user information from the github client
        github_username = github_user.data['login']   # we first give the user data property of github_user
        # and then access the login field that has the username
        
        user = UserModel.find_by_username(github_username)
        if not user:
            user = UserModel(username=github_username, password=None)
            user.save_to_db()  
            access_token = create_access_token(identity =user.id,fresh=True)
            refresh_token = create_refresh_token(user.id) # user.id is the identity
            return {'access_token':access_token,'refresh_token':refresh_token},200
            # note: this user can't access our resources if he tries to pass through our login resource
            # because he does not have a password but with github it is possible

# g is a global object that can be accessed anywhere in our flask app. whatever is placed in it can be used anywhere