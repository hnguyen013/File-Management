from models.linked_list import LinkedList
from datetime import datetime

class Node:

    def __init__(self,name,is_folder,size=0):
        self.name = name
        self.is_folder = is_folder
        self.size = size
        self.parent = None
        self.children = LinkedList()
        self.created_at = datetime.now()

    def get_size(self):
        if not self.is_folder:
            return self.size
        total = 0
        for child in self.children:
            total += child.get_size()
        return total

    def get_type(self):
        if self.is_folder:
            return "Folder"
        return "File"
    
    def get_created_at(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M")