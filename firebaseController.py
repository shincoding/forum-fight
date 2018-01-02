import pyrebase

# THE API
def authentication():
  config = {
    "apiKey": "API KEY",
    "authDomain": "AUTHOR DOMAIN",
    "databaseURL": "DATABASE URL",
    "storageBucket": "STORAGE BUCKET LINK"
  }
  firebase = pyrebase.initialize_app(config)

  # Get a reference to the auth service
  auth = firebase.auth()

  # Log the user in
  user = auth.sign_in_with_email_and_password("FIREBASE EMAIL", "FIREBASE PASSWORD")

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
