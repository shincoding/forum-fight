import praw
import config
import random
import pymysql

conn = pymysql.connect("sql3.freemysqlhosting.net", "sql3187319", "r1VDIBw4lj", "sql3187319")

cur = conn.cursor()
cur.execute("SELECT id, comments, player1, player2 FROM battles")



class Comment_Link_Node:
    """ Initialze Linked List Node.
    """
    def __init__(self, comment, user, prev=None, next=None):
        self.next = next
        self.prev = prev
        self.comment = comment
        self.user = user


class Comment_Linked_List:
    """ Initialze Linked List.
    """
    def __init__(self):
        self.front, self.back,self.size = None, None, 0

    def append(self, comment, user):
        # create the new node
        new_node = Comment_Link_Node(comment, user)
        # if the list is empty, the new node is front and back
        if self.size == 0:
            assert self.back is None and self.front is None, "ooops"
            self.front = self.back = new_node
        # if the list isn't empty, front stays the same
        else:
            # change *old* self.back.next_ first!!!!
            self.back.next = new_node
            self.back.next.prev = self.back
            self.back = new_node
        # remember to increase the size
        self.size += 1


class Player:
    """ Initialze Player.
    """
    def __init__(self, id):
        self.id = id
        self.hp = 10
        self.state = True
        self.current_comment = None


    def attack(self, value):
        int_value = int(value)
        attacked_value = abs(int_value - random.randint(0, 9))
        return attacked_value

    def defend(self, value, attack_value):
        int_value = int(value)
        int_attack_Value = int(attack_value)
        defend_value = abs(int_value - random.randint(0, 9))
        self.hp -= abs(defend_value-int_attack_Value)
        if self.hp < 1:
            self.state = False
        return abs(defend_value-int_attack_Value)


def hp_change(comments, player1, player2):
    """ Change hp.

    @param Comment_Linked_List comments:
    @param Player player1:
    @param Player player2:
    @rtype: None
    """
    cur_comment = comments.front
    while cur_comment is not None:
        if "damaged" in cur_comment.comment and player1 in cur_comment.comment:
            player1.hp -= cur_comment.comment.split()[-1]
        if "damaged" in cur_comment.comment and player2 in cur_comment.comment:
            player2.hp -= cur_comment.comment.split()[-1]
        cur_comment = cur_comment.next

    return None



def go_to_current(first_reddit_comment, comments):
    """ Go th current comment (bot).

    @param praw.models.Comment first_reddit_comment:
    @param Comment_Linked_List comments:
    @rtype: (string, string)
    """
    cur_comment = comments.front

    def _private(first_reddit_comment, cur_comment):
        for reddit_comment in first_reddit_comment.replies:
            if cur_comment.text == reddit_comment.body:
                if comments.back.comment == reddit_comment.body and comments.back.user == cur_comment.author.name:
                    tuple_ = (reddit_comment.author.name, reddit_comment)
                    return tuple_
                else:
                    cur_comment = cur_comment.next
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


def comment_to_reply(last_comment, player1, player2, command):
    """ Go through all the comments.

    @param (string, string) last_comment:
    @param Player player1:
    @param Player player2:
    @param (string, string) command:
    @rtype: string
    """
    # I attack for 5
    # I defend for 3
    if "attack" in last_comment[1]:
        damage = player1.attack(last_comment[1].split()[2])
        return last_comment[0] + " has damaged:" + damage
    if "defend" in last_comment[1]:
        if last_comment[0] == player1.id:
            damage = player1.defend(last_comment[1].split()[2],command[1].body[command[1].body.find("damaged:")+1:])
            if player1.hp < 1:
                return player1.id + " is dead."
            else:
                return player1.id + " has been damaged " + damage
        if last_comment[0] == player2.id:
            damage = player2.defend(last_comment[1].split()[2],command[1].body[command[1].body.find("damaged:")+1:])
            if player2.hp < 1:
                return player2.id + " is dead."
            else:
                return player2.id + " has been damaged " + damage




def bot_login():
    """ Log in.

    @rtype: praw.Reddit
    """
    r = praw.Reddit(username = config.username, password = config.password,
                client_id = config.client_id, client_secret = config.client_secret, user_agent = "dsafsdafsafjdsl")
    return r

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
        if comment.body == "I attack 3":
            print("xx")
        check_comment(comment, list_ids, list_comments, list_player1, list_player2)
        recursion_comments(comment, list_ids, list_comments, list_player1, list_player2)


def check_comment(comment, list_ids, list_comments, list_player1, list_player2):
    """ This is what happens when you check the comment.

    @param praw.models.Comment comment:
    @param list list_ids:
    @rtype: None
    """
    if comment.fullname in list_ids:
        return None

    # if id matches up.
    if comment.body.split()[0] in list_ids:
        id = comment.body.split()[0]
        num = list_ids.index(id)
        player1 = Player(list_player1[num])
        player2 = Player(list_player2[num])
        linked_commments = create_linked_list(list_comments[num])
        # this is the current comment (by the bot)
        current_comment = go_to_current(comment, linked_commments)
        # change hp
        hp_change(linked_commments, player1, player2)

        # list of replies
        if current_comment is None:
            return None
        replies = current_comment[1].replies
        correct_reply = None
        for reply in replies:
            if "Continued game:" in reply.body and reply.author.name == player1.id or reply.author.name == player2.id:
                correct_reply = (reply.author.name, reply.body)
        what_to_reply = comment_to_reply(correct_reply, player1, player2, current_comment)
        correct_reply[1].reply(what_to_reply)
        # add data

        updated_comment = list_comments[num] + correct_reply[0] + "%" + correct_reply[1].body + "$" + "com%" + what_to_reply + "$"
        cur.execute("""
                   UPDATE battles
                   SET id=%s, comments=%s, player1=%s, player2=%s
                   WHERE id='%s'
                """, (comment.body, updated_comment, list_player1[num], list_player2[num], comment.body))

    if "I initiate the reddit game:" in comment.body:
        code = comment.fullname
        chosen = comment.body[comment.body.find(":") + 1:]
        comment_for_add = "comp%" + code + " begin game.$"
        sql = "insert into battles (id, comments, player1, player2) VALUES('%s', '%s', '%s', '%s')" % \
              (code, comment_for_add, comment.author.name, chosen)
        cur.execute(sql)
        comment.reply(code + " begin game.")

    conn.commit()


def begin_game(r):
    """ This is where game will start.

    @param praw.Reddit r: this is the reddit api info.
    @rtype: None
    """
    # list of ids
    list_ids = []
    # list of comments
    list_comments = []
    # list of player 1
    list_player1 = []
    # list of player2
    list_player2 = []
    cur2 = conn.cursor()
    cur2.execute("SELECT id, comments, player1, player2 FROM battles")
    for (id, comments, player1, player2) in cur2:
        # fill in the lists from the database.
        list_ids.append(id)
        list_comments.append(comments)
        list_player1.append(comments)
        list_player2.append(comments)
    for id in list_ids:
        print(id)
    cur2.close()
    # check all the comments in the subreddit. Will need to use recursion later.
    for comment in r.subreddit("test").comments(limit=25):
        comment.refresh()
        check_comment(comment, list_ids, list_comments, list_player1, list_player2)
        recursion_comments(comment, list_ids, list_comments, list_player1, list_player2)

r = bot_login()
begin_game(r)


cur.close()
conn.close()
