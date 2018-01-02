import pyrebase

# THE API
def authentication():
  config = {
    "apiKey": "AIzaSyBxEYvR1M4vH8Y646axohmyS1H0-6lsZC8",
    "authDomain": "projectId.firebaseapp.com",
    "databaseURL": "https://forum-fight.firebaseio.com",
    "storageBucket": "gs://forum-fight.appspot.com"
  }
  firebase = pyrebase.initialize_app(config)

  # Get a reference to the auth service
  auth = firebase.auth()

  # Log the user in
  user = auth.sign_in_with_email_and_password("freedatabase123@gmail.com", "thisisafreedatabase")

  # Get a reference to the database service
  return firebase.database()


def addData(id, comments, player1, player2):
  db = authentication()
  data = {"comments": comments, "player1": player1, "player2": player2}
  db.child("battles").child(id).set(data)

def updateData(id, comments, player1, player2):
  db = authentication()
  data = {"comments": comments, "player1": player1, "player2": player2}
  db.child("battles").child(id).update(data)

def getData():
  db = authentication()
  return db.child("battles").get().each()

def getComments(id):
  for data in getData():
    if data.key() == id:
      return data.val().get("comments")
  return None
