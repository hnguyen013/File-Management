from models.node import Node


class FileSystemTree:

    def __init__(self):
        self.root = Node("/", True)
        self.current_working_dir = self.root
    
    def mkdir(self, name):
        folder = Node(name=name,is_folder=True)
        folder.parent = self.current_working_dir
        self.current_working_dir.children.append(folder)

    def create_file(self,name,size):
        file = Node(name=name,is_folder=False,size=size)
        file.parent = self.current_working_dir
        self.current_working_dir.children.append(file)

    def ls(self):
        items = []
        for child in self.current_working_dir.children:
            items.append(child)
        return items

    def pwd(self):
        current = self.current_working_dir
        path = []
        while current != self.root:
            path.append(current.name)
            current = current.parent
        path.reverse()
        if not path:
            return "/"
        return "/" + "/".join(path)
    
    def cd(self, name):
        if name == "..":
            if self.current_working_dir.parent:
                self.current_working_dir = (self.current_working_dir.parent)
            return True
        target = (self.current_working_dir.children.find_by_name(name))
        if target and target.is_folder:
            self.current_working_dir = target
            return True
        return False
    
    def search(self, name):
        return self._dfs_search(self.root,name)

    def _dfs_search(self,node,name):
        if node.name == name:
            return node
        for child in node.children:
            result = self._dfs_search(child,name)
            if result:
                return result
        return None
    
    def search_all(self, name):
        results = []
        self._dfs_search_all(self.root,name,results)
        return results
    
    def _dfs_search_all(self,node,name,results):
        if node.name == name:
            results.append(node)
        for child in node.children:
            self._dfs_search_all(child,name,results)
    
    def tree(self):
        self._print_tree(self.root,"")

    def _print_tree(self,node,prefix):
        print(prefix + node.name)
        children = list(node.children)
        for i, child in enumerate(children):
            if i == len(children) - 1:
                self._print_tree(child,prefix + "    ")
            else:
                self._print_tree(child,prefix + "|   ")
    
    def delete_recursive(self,node):
        for child in list(node.children):
            self.delete_recursive(child)
        if node.parent:
            node.parent.children.remove(node)

    def delete(self, name):
        target = (self.current_working_dir.children.find_by_name(name))
        if target:
            self.delete_recursive(target)
            return True
        return False
    
    def rename(self, old_name, new_name):
        for child in self.current_working_dir.children:
            if child.name == new_name:
                raise ValueError("Name already exists")
        for child in self.current_working_dir.children:
            if child.name == old_name:
                child.name = new_name
                return True
        return False
    def go_root(self):
        self.current_working_dir = self.root