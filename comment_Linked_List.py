from comment_Link_Node import Comment_Link_Node

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
