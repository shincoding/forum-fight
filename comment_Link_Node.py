class Comment_Link_Node:
    """ Initialze Linked List Node.
    """
    def __init__(self, comment, user, prev=None, next=None):
        self.next = next
        self.prev = prev
        self.comment = comment
        self.user = user
