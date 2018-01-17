import praw
import config
from game import *


def begin_game(r):
    """ This is where game will start.

    @param praw.Reddit r: this is the reddit api info.
    @rtype: None
    """
    # list of ids
    list_ids = []
    # list of comments
    list_comments_codes = []
    # list of player 1
    list_player1 = []
    # list of player2
    list_player2 = []
    firebaseData = firebaseController.getData()
    if firebaseData is not None:
        for data in firebaseData:
            list_ids.append(data.key())
            list_comments_codes.append(data.val().get("comments"))
            list_player1.append(data.val().get("player1"))
            list_player2.append(data.val().get("player2"))
        # check all the comments in the subreddit. Not using recursion at the moment.
        for submission in r.subreddit('test').hot(limit=10):
            submission.comments.replace_more(limit=None, threshold=0)
            for comment in submission.comments.list():
                check_comment(comment, list_ids, list_comments_codes, list_player1, list_player2)


def bot_login():
    """ Log in.

    @rtype: praw.Reddit
    """
    r = praw.Reddit(username = config.username, password = config.password,
                client_id = config.client_id, client_secret = config.client_secret, user_agent = "dsafsdafsafjdsl")
    return r

r = bot_login()
begin_game(r)
