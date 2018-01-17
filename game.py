from player import Player
from comment_Linked_List import Comment_Linked_List
import firebaseController


def hp_change(comment, player1, player2):
    """ Change hp.

    @param Comment_Linked_List comment:
    @param Player player1:
    @param Player player2:
    @rtype: None
    """

    if "damaged" in comment and player1.id in comment:
        player1.hp -= int(comment.split()[-3].strip("."))
    if "damaged" in comment and player2.id in comment:
        player2.hp -= int(comment.split()[-3].strip("."))

    return None



def go_to_current(first_reddit_comment, comments, player1, player2):
    """ Go to the current comment (of bot). Change the hp of the players.

    @param praw.models.Comment first_reddit_comment:
    @param Comment_Linked_List comments:
    @rtype: (string, praw.models.Comment)
    """
    cur_comment = comments.front

    def _private(first_reddit_comment, cur_comment):
        if first_reddit_comment.fullname == cur_comment.comment:
            if comments.back.comment == first_reddit_comment.fullname and comments.back.user == cur_comment.user:
                tuple_ = (first_reddit_comment.author.name, first_reddit_comment)
                hp_change(first_reddit_comment.body, player1, player2)
                return tuple_
            else:
                cur_comment = cur_comment.next
                for reddit_comment in first_reddit_comment.replies:
                    hp_change(first_reddit_comment.body, player1, player2)
                    return _private(reddit_comment, cur_comment)
        return None
    return _private(first_reddit_comment, cur_comment)

def create_linked_list(text):
    """ Create linked list

    @param string text:
    @rtype: Comment_Linked_List
    """
    lst = Comment_Linked_List()
    def _private(text):
        if "$" in text:
            node_text = text[0:text.find("$")]
            splited = node_text.split("%")
            lst.append(splited[1], splited[0])
            if len(text) != text.find("%") + 1:
                return _private(text[text.find("$")+1:])
    _private(text)
    return lst


def comment_to_reply(last_comment, player1, player2):
    """ Return string based on last comment.

    @param (string, string) last_comment:
    @param Player player1:
    @param Player player2:
    @rtype: string
    """
    if "attack" in last_comment.body:
        damage = player1.attack(last_comment.body.split()[-1])
        return last_comment.author.name + " has damaged: " + str(damage) + "."
    if "defend" in last_comment.body:
        if last_comment.author.name == player1.id:
            damage = player1.defend(last_comment.body.split()[-1])
            if player1.hp < 1:
                return player1.id + " is dead."
            else:
                return player1.id + " has been damaged: " + str(damage) + '.'
        if last_comment.author.name == player2.id:
            damage = player2.defend(last_comment.body.split()[-1])
            if player2.hp < 1:
                return player2.id + " is dead."
            else:
                return player2.id + " has been damaged: " + str(damage) + "."






def recursion_comments(first_comments, list_ids, list_comments, list_player1, list_player2):
    """ Go through all the comments.

    @param praw.models.Comment first_comments:
    @param list list_ids:
    @param list list_comments:
    @param list list_player1:
    @param list list_player2:
    @rtype: None
    """
    for comment in first_comments.replies:

        check_comment(comment, list_ids, list_comments, list_player1, list_player2)
        recursion_comments(comment, list_ids, list_comments, list_player1, list_player2)


def check_comment(comment, list_ids, list_comments_codes, list_player1, list_player2):
    """ This is what happens when you check the comment.

    @param praw.models.Comment comment:
    @param list list_ids:
    @rtype: None
    """
    # if the comment does not initiate the game
    if comment.fullname in list_ids:
        return None

    if "I initiate the reddit game:" in comment.body:
        code = comment.fullname
        chosen = comment.body[comment.body.find(":") + 1:].strip()
        REPLY_BY_BOT = comment.reply(code + " begin game. " + chosen + " proceed.")
        REPLY_DATA = "comp%" + REPLY_BY_BOT.fullname + "$"
        firebaseController.addData(code, REPLY_DATA, comment.author.name, chosen)
        return None

    # if id matches up.
    if comment.body.split()[0] in list_ids:
        # the first word in the comment represents the id of the game
        ID = comment.body.split()[0]
        ARRAY_POSITION = list_ids.index(ID)
        player1 = Player(list_player1[ARRAY_POSITION])
        player2 = Player(list_player2[ARRAY_POSITION])
        linked_commments = create_linked_list(list_comments_codes[ARRAY_POSITION])
        # this is the current comment (by the bot)
        current_comment = go_to_current(comment, linked_commments, player1, player2)
        if current_comment is None:
            return None
        # list of replies
        if current_comment is None:
            return None
        replies = current_comment[1].replies
        correct_reply = None
        for reply in replies:
            if "Continued game:" in reply.body and (reply.author.name == player1.id or reply.author.name == player2.id) and current_comment[1].body.split()[-2] == reply.author.name:
                correct_reply = reply
        if correct_reply is None:
            return None
        if correct_reply.fullname in firebaseController.getComments(comment.body.split()[0]):
            return None
        if correct_reply.author.name == player1.id:
            REPLY_BY_BOT = correct_reply.reply(id + " " + comment_to_reply(correct_reply, player1, player2) + " " + player2.id + " proceed.")
        else:
            REPLY_BY_BOT = correct_reply.reply(id + " " + comment_to_reply(correct_reply, player1, player2) + " " + player1.id + " proceed.")
        # add data

        REPLY_DATA = list_comments_codes[ARRAY_POSITION] + correct_reply.author.name + "%" + correct_reply.fullname + "$" + "comp%" + REPLY_BY_BOT.fullname + "$"
        firebaseController.updateData(comment.body.split()[0], REPLY_DATA, list_player1[ARRAY_POSITION], list_player2[ARRAY_POSITION])
        return None
