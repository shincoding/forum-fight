import praw
import config
import random
import pymysql

conn = pymysql.connect("sql3.freemysqlhosting.net", "sql3187319", "r1VDIBw4lj", "sql3187319")

# host="mysql177321.crkixep6a1mw.us-east-2.rds.amazonaws.com"
# port=3306
# dbname="mySQL177321"
# user="user_177321"
# password="password177321"
#
# conn = pymysql.connect(host, user=user,port=port,
#                            passwd=password, db=dbname)

cur = conn.cursor()
cur.execute("SELECT * FROM battles")



class Comment_Link_Node:
    def __init__(self, comment, user, prev=None, next=None):
        self.next = next
        self.prev = prev
        self.comment = comment
        self.user = user


class Comment_Linked_List:
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
    def __init__(self, id):
        self.id = id
        self.hp = 10
        self.state = True
        self.current_comment = None


    def attack(self, value):
        attacked_value = abs(value - random.randint(0, 9))
        return attacked_value

    def defend(self, value, attack_value):
        defend_value = abs(value - random.randint(0, 9))
        self.hp -= abs(defend_value-attack_value)
        if self.hp < 1:
            self.state = False
        return None


def hp_change(comments, player1, player2):
    #number of attacks and defends counter

    cur_comment = comments.front
    while cur_comment is not None:
        if "damaged" in cur_comment.comment and player1 in cur_comment.comment:
            player1.hp -= 3
        if "damaged" in cur_comment.body and player2 in cur_comment.comment:
            player2.hp -= 3
        cur_comment = cur_comment.next

    return None



def go_to_current(first_reddit_comment, comments):
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
    r = praw.Reddit(username = config.username, password = config.password,
                client_id = config.client_id, client_secret = config.client_secret, user_agent = "dsafsdafsafjdsl")
    return r

def begin_game(r):
    # list of ids
    list_ids = []
    # list of comments
    list_comments = []
    # list of player 1
    list_player1 = []
    # list of player2
    list_player2 = []
    for (id, comments, player1, player2) in cur:
        # fill in the lists from the database.
        list_ids.append(id)
        list_comments.append(comments)
        list_player1.append(comments)
        list_player2.append(comments)
    # check all the comments in the subreddit. Will need to use recursion later.
    for comment in r.subreddit("test").comments(limit=25):
        # if id matches up.
        if  comment.body.split()[0] in list_ids:
            id = comment.body.split()[0]
            infos = cur.execute("SELECT comments, player1, player 2 from battles where id=%s" % id)
            player1 = Player(infos[1])
            player2 = Player(infos[2])
            linked_commments = create_linked_list(infos[0])
            # this is the current comment (by the bot)
            current_comment = go_to_current(comment, linked_commments)
            # change hp
            hp_change(linked_commments, player1, player2)

            # list of replies
            replies = current_comment[1].replies
            correct_reply = None
            for reply in replies:
                if "Continued game:" in reply.body and reply.author.name == player1.id or reply.author.name == player2.id:
                    correct_reply = (reply.author.name, reply.body)
            what_to_reply = comment_to_reply(correct_reply, player1, player2, current_comment)
            correct_reply[1].reply(what_to_reply)
            #add data

            updated_comment = infos[0] + correct_reply[0] + "%" + correct_reply[1].body + "$" + "com%" + what_to_reply + "$"
            cur.execute("""
               UPDATE battles
               SET id=%s, comments=%s, player1=%s, player2=%s
               WHERE id=%s
            """, (comment.body, updated_comment, infos[1], infos[2], comment.body))



        if "I initiate the reddit game:" in comment.body:
            code = comment.fullname
            chosen = comment.body[comment.body.find(":")+1:]
            comment_for_add = "comp%" + code + " begin game.$"
            sql = "insert into battles VALUES('%s', '%s', '%s', %d)" % \
                  (code, comment_for_add, comment.author.name, chosen)
            cur.execute(sql)
            comment.reply(code + " begin game.")


r = bot_login()

#begin_game(r)



cur.close()
conn.close()

#http://praw.readthedocs.io/en/latest/code_overview/models/comment.html?highlight=comment

#replies

# def recursion1(current_comment):
#     #number of attacks and defends counter
#     lst = []
#     lst2 = []
#     (lst.append(current_comment[4]) if "attacked" in current_comment else None)
#     (lst2.append(current_comment[4]) if "defend" in current_comment else None)
#
#
#     for com in current_comment:
#         lst.append(recursion1(com)[0])
#         lst2.papend(recursion1(com)[1])
#
#     tuple_ = (sum(lst), sum(lst2))
#     return tuple_

# def recursion(r, num, comments, player1, player2):
#     for comment in r.subreddit("test").comments(limit=25):
#         if comments[num] == comment:
#             if len(comments) == num + 1:
#                 return comment
#             return recursion(r, num + 1, comments)
#     #go to the current comment. And do something.


#keep going with timer

#linked list
# comment 1 <--> comment 2
# next, player, content
