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


def comment_to_reply(last_comment, player1, player2):

    if "blah" in last_comment and last_comment:
        player1.attack()
    if "blah" in last_comment:
        player2.defend()
    if player1.hp <=0:
        return "He ded"
    if player2.hp <=0:
        return 'He ded'




def bot_login():
    r = praw.Reddit(username = config.username, password = config.password,
                client_id = config.client_id, client_secret = config.client_secret, user_agent = "dsafsdafsafjdsl")
    return r

def begin_game(r):
    list_ids = []
    list_comments = []
    list_player1 = []
    list_player2 = []
    for (id, comments, player1, player2) in cur:
        list_ids.append(id)
        list_comments.append(comments)
        list_player1.append(comments)
        list_player2.append(comments)

    for comment in r.subreddit("test").comments(limit=25):
        if  comment.body in list_ids:
            id = comment.body.split()[0]
            infos = cur.execute("SELECT comments, player1, player 2 from battles where id=%s" % (comment.body))
            player1 = Player(infos[1])
            player2 = Player(infos[2])
            comments = create_linked_list(infos[0])
            current_comment = go_to_current(comment, comments)
            hp_change(comments, player1, player2)

            lsst = current_comment[1].replies
            added_comment = None
            for comment in lsst:
                if "Continued game:" in comment and comment.author.name == player1.id or comment.author.name == player2.id:
                    added_comment = (comment.author.name, comment)
            what_to_reply = comment_to_reply(added_comment, player1, player2)
            added_comment[1].reply(what_to_reply)
            #add data

            updated_comment = infos[0] + added_comment[0] + "%" + added_comment[1].body + "$" + "com%" + what_to_reply + "$"
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
