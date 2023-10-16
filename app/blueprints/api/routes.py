from flask import request, jsonify
from . import bp
from app.models import User, Scores_Table

# verify a user
@bp.post('/verifyuser')
def api_verify_user():
  content = request.json
  thisUsername = content['username']
  thisPassword = content['password']
  thisUser = User.query.filter_by(username=thisUsername).first()
  if thisUser and thisUser.check_password(thisPassword):
    return jsonify({'userToken': thisUser.token}), 200
  return jsonify({'error':'badCredentials'}), 401


# register a user
@bp.post('/newuser')
def api_new_user():
  content = request.json
  thisUsername = content['username'] # written like this assuming we're keying into a passed in json obj
  thisEmail = content['email'] # again, this is all predicated on user posting a json file here.
  thisPassword = content['password']
  thisUserCheck = User.query.filter_by(username=thisUsername).first()
  if thisUserCheck:
    return jsonify({'error':'duplicateUser'}), 401
  thisEmailCheck = User.query.filter_by(email=thisEmail).first()
  if thisEmailCheck:
    return jsonify({'error':'duplicateEmail'}), 401
  thisNewUser = User(email = thisEmail, username=thisUsername)
  thisNewUser.password = thisNewUser.hash_password(thisPassword)
  thisNewUser.add_token()
  thisNewUser.commit()
  return jsonify({'message': "registerSuccess"}), 200

# receive all game scores
@bp.get('/scores')
def api_scores():
  result = []
  # add to this list all games in database
  theseGames = Scores_Table.query.all() # .all() is returning all posts, where is post is a class
  for eachGame in theseGames:
    result.append({'game_id': eachGame.game_id,
                   'game_score':eachGame.game_score,
                   'game_date': eachGame.game_date,
                   'username': eachGame.username})
  return jsonify(result), 200 # this 200 is returning a "success" status

# receive all scores from a single user
@bp.get('/scores/<username>')
def user_scores(username):
  thisUser = User.query.filter_by(username=username).first().user_id
  if thisUser: # if they give us a username we query for it, if there's no match then the username give was invalid
    theseGames = Scores_Table.query.filter_by(user_id=thisUser)
    result=[]
    for eachGame in theseGames:
      result.append({'game_id': eachGame.game_id,
                     'game_score':eachGame.game_score,
                     'game_date': eachGame.game_date,
                     'username': eachGame.username})
    return jsonify(result), 200 # this 200 is returning a "success" status
  return jsonify({'error':"noSuchUser"}), 401

# Log a new completed game score
@bp.post('/newScore')
def log_newScore():
  try:
    # receive the post data for logging a new game. 
    # Front end will send only a token and a game score.
    thisContent = request.json
    thisToken = thisContent.get('token')
    thisGameScore = int(thisContent.get('game_score'))
    # handle case in which anonymous score was logged. This is 
    # from a non-signed in user, and front end has sent as the token
    # the string "anonymous". Todd entered "anonymous" as a user in
    # the user table, but is not hard coding the user ID in case
    # we reset that table in the future and create a new "anonymous"
    # user.
    if thisToken == "anonmyous":
      thisUserId = User.query.filter_by(username="anonymous").first().user_id
      thisUsername = "anonymous"
    else:
      # use the token to retrieve user info from user table
      # then add that data as a new post to the scores table
      thisUser = User.query.filter_by(token=thisToken).first()
      thisUserId = thisUser.user_id
      thisUsername = thisUser.username
    # add all data to Scores Table
    thisNewGame = Scores_Table(user_id = thisUserId,
                               username = thisUsername,
                               game_score = thisGameScore)
    # commit post
    thisNewGame.commit()
    # return message
    return jsonify({'message':'addedScore'}), 200
  except:
    return jsonify({'error': 'errorAddingScore'}), 401