from views.styles import APP_STYLE
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QInputDialog,
    QSplitter,
    QTreeWidget,
    QLineEdit,
    QTreeWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QComboBox,
    QMenu,
    QApplication,
    QStyle,
    QAbstractItemView,
    QGroupBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from models.file_system_tree import FileSystemTree


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(APP_STYLE)
        self.fs = FileSystemTree()
        self.fs.load_from_json() # Đọc dữ liệu JSON cũ lên nếu có

        self.setWindowTitle("File System Management")
        self.setGeometry(100, 50, 1200, 750)

        self.folder_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        self.file_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)

        self.init_ui()
        self.refresh_view()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 1. Main Toolbar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.btn_new_folder = QPushButton("New Folder")
        self.btn_new_file = QPushButton("New File")
        self.btn_rename = QPushButton("Rename")
        self.btn_delete = QPushButton("Delete")
        self.btn_refresh = QPushButton("Refresh")

        self.btn_new_folder.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        self.btn_new_file.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.btn_delete.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        self.btn_refresh.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))

        button_layout.addWidget(self.btn_new_folder)
        button_layout.addWidget(self.btn_new_file)
        button_layout.addWidget(self.btn_rename)
        button_layout.addWidget(self.btn_delete)
        button_layout.addWidget(self.btn_refresh)
        
        button_layout.addStretch()
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Sort by Name", "Sort by Date", "Sort by Size", "Sort by Type"])
        self.sort_combo.setMinimumWidth(150)
        button_layout.addWidget(self.sort_combo)

        main_layout.addLayout(button_layout)

        # 2. Navigation + Search Bar
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(8)

        self.btn_back = QPushButton("Back")
        self.btn_root = QPushButton("Home")

        nav_layout.addWidget(self.btn_back)
        nav_layout.addWidget(self.btn_root)
        nav_layout.addWidget(QLabel("Path:"))

        self.path_label = QLineEdit("/")
        self.path_label.setReadOnly(True)
        nav_layout.addWidget(self.path_label, 3)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search file or folder...")
        self.search_input.setMinimumWidth(220)

        self.btn_search = QPushButton("🔍 Search")

        nav_layout.addWidget(self.search_input, 1)
        nav_layout.addWidget(self.btn_search)

        main_layout.addLayout(nav_layout)

        # 3. Content Area: Tree Widget and Table Widget
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(8)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Folder Tree")
        self.tree_widget.itemClicked.connect(self.open_from_tree)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Name", "Type", "Created", "Size"])
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        splitter.addWidget(self.tree_widget)
        splitter.addWidget(self.table_widget)
        splitter.setSizes([280, 920])

        main_layout.addWidget(splitter, 1)

        # 4. Information Panel
        info_group = QGroupBox("Selected Item Information")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        info_layout.setContentsMargins(15, 12, 15, 12)

        self.info_name = QLabel("Name:")
        self.info_type = QLabel("Type:")
        self.info_path = QLabel("Path:")
        self.info_size = QLabel("Size:")
        self.info_date = QLabel("Created:")

        info_layout.addWidget(self.info_name)
        info_layout.addWidget(self.info_type)
        info_layout.addWidget(self.info_path)
        info_layout.addWidget(self.info_size)
        info_layout.addWidget(self.info_date)

        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Event Connections
        self.btn_new_folder.clicked.connect(self.add_folder)
        self.btn_new_file.clicked.connect(self.add_file)
        self.btn_delete.clicked.connect(self.delete_item)
        self.btn_refresh.clicked.connect(self.refresh_view)
        self.sort_combo.currentIndexChanged.connect(self.refresh_view)
        self.btn_back.clicked.connect(self.go_back)
        self.btn_root.clicked.connect(self.go_root)
        self.btn_search.clicked.connect(self.search_item)
        self.btn_rename.clicked.connect(self.rename_item)
        self.table_widget.cellDoubleClicked.connect(self.open_folder)
        self.table_widget.itemSelectionChanged.connect(self.update_info_panel)
        self.table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self.show_context_menu)

    def format_size(self, size_in_bytes):
        try:
            size = float(size_in_bytes)
        except (ValueError, TypeError):
            return "0 B"
            
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                if unit == 'B':
                    return f"{int(size)} {unit}"
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def refresh_view(self):
        self.path_label.setText(self.fs.pwd())

        self.table_widget.setRowCount(0)
        self.tree_widget.clear()

        root_item = QTreeWidgetItem(["/"])
        self.tree_widget.addTopLevelItem(root_item)

        self.add_tree_items(root_item, self.fs.root)
        self.tree_widget.expandAll()

        items = self.fs.ls()
        sort_mode = self.sort_combo.currentText()

        if sort_mode == "Sort by Name":
            items.sort(key=lambda x: x.name.lower())
        elif sort_mode == "Sort by Date":
            items.sort(key=lambda x: x.created_at, reverse=True)
        elif sort_mode == "Sort by Size":
            items.sort(key=lambda x: x.get_size(), reverse=True)
        elif sort_mode == "Sort by Type":
            items.sort(key=lambda x: x.get_type())

        for child in items:
            row = self.table_widget.rowCount()
            self.table_widget.insertRow(row)

            # Cột Name
            name_item = QTableWidgetItem(child.name)
            if child.get_type() == "Folder":
                name_item.setIcon(self.folder_icon)
            else:
                name_item.setIcon(self.file_icon)
            self.table_widget.setItem(row, 0, name_item)

            # Cột Type
            type_item = QTableWidgetItem(child.get_type())
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row, 1, type_item)

            # Cột Created
            created_item = QTableWidgetItem(child.get_created_at())
            created_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row, 2, created_item)

            # Cột Size
            if child.get_type() == "Folder":
                size_text = "-"
            else:
                size_text = self.format_size(child.get_size())
                
            size_item = QTableWidgetItem(size_text)
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row, 3, size_item)

    def add_folder(self):
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and name:
            try:
                self.fs.mkdir(name)
                self.fs.save_to_json()  # <-- Tự động lưu sau khi tạo folder
                self.refresh_view()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def add_file(self):
        name, ok = QInputDialog.getText(self, "New File", "File name:")
        if ok and name:
            size, ok_size = QInputDialog.getInt(self, "File Size", "Size (Bytes):", 0, 0)
            if ok_size:
                try:
                    self.fs.create_file(name, size)
                    self.fs.save_to_json()  # <-- Tự động lưu sau khi tạo file
                    self.refresh_view()
                except ValueError as e:
                    QMessageBox.warning(self, "Error", str(e))

    def delete_item(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select an item")
            return

        name = self.table_widget.item(selected_row, 0).text()
        result = self.fs.delete(name)
        if result:
            self.fs.save_to_json()  # <-- Tự động lưu sau khi xóa thành công
            self.refresh_view()
        else:
            QMessageBox.warning(self, "Error", "Cannot delete item")

    def go_back(self):
        self.fs.cd("..")
        self.refresh_view()

    def search_item(self):
        name = self.search_input.text().strip()
        if not name:
            return

        results = self.fs.search_all(name)
        if not results:
            QMessageBox.warning(self, "Not Found", "Item not found")
            return

        text = ""
        for item in results:
            path = []
            current = item
            while current.parent:
                path.append(current.name)
                current = current.parent
            path.reverse()
            text += f"{item.get_type()} : /{'/'.join(path)}\n"

        QMessageBox.information(self, "Search Result", text)

    def open_folder(self, row, column):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select a folder")
            return

        name = self.table_widget.item(selected_row, 0).text()
        item_type = self.table_widget.item(selected_row, 1).text()

        if item_type != "Folder":
            QMessageBox.warning(self, "Error", "Please select a folder, not a file")
            return

        result = self.fs.cd(name)
        if result:
            self.refresh_view()
        else:
            QMessageBox.warning(self, "Error", "Cannot open folder")

    def go_root(self):
        self.fs.go_root()
        self.refresh_view()

    def add_tree_items(self, parent_item, folder_node):
        for child in folder_node.children:
            if child.get_type() == "Folder":
                tree_item = QTreeWidgetItem([child.name])
                tree_item.setIcon(0, self.folder_icon)
                parent_item.addChild(tree_item)
                self.add_tree_items(tree_item, child)

    def open_from_tree(self, item, column):
        path_parts = []
        current = item
        while current:
            path_parts.insert(0, current.text(0))
            current = current.parent()

        if path_parts and path_parts[0] == "/":
            path_parts.pop(0)

        self.fs.go_root()
        for folder in path_parts:
            self.fs.cd(folder)
        self.refresh_view()

    def show_context_menu(self, pos):
        menu = QMenu()
        add_folder = menu.addAction("New Folder")
        add_file = menu.addAction("New File")
        menu.addSeparator()
        rename_action = menu.addAction("Rename")
        delete_item = menu.addAction("Delete")

        action = menu.exec(self.table_widget.viewport().mapToGlobal(pos))
        if action == add_folder:
            self.add_folder()
        elif action == add_file:
            self.add_file()
        elif action == delete_item:
            self.delete_item()
        elif action == rename_action:
            self.rename_item()

    def rename_item(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select an item")
            return

        old_name = self.table_widget.item(selected_row, 0).text()
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=old_name)
        if not ok:
            return
        new_name = new_name.strip()

        if not new_name:
            QMessageBox.warning(self, "Error", "Name cannot be empty")
            return
        try:
            self.fs.rename(old_name, new_name)
            self.fs.save_to_json()  # <-- Tự động lưu sau khi đổi tên thành công
            self.refresh_view()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def update_info_panel(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0:
            return

        name = self.table_widget.item(selected_row, 0).text()
        current_items = self.fs.ls()
        selected_item = None

        for item in current_items:
            if item.name == name:
                selected_item = item
                break

        if selected_item is None:
            return

        self.info_name.setText(f"Name: {selected_item.name}")
        self.info_type.setText(f"Type: {selected_item.get_type()}")
        
        formatted_total_size = self.format_size(selected_item.get_size())
        self.info_size.setText(f"Size: {formatted_total_size}")
        
        self.info_date.setText(f"Created: {selected_item.get_created_at()}")

        current_path = self.fs.pwd()
        if current_path == "/":
            full_path = f"/{selected_item.name}"
        else:
            full_path = f"{current_path}/{selected_item.name}"
        self.info_path.setText(f"Path: {full_path}")

    def closeEvent(self, event):
        """Bắt sự kiện tắt ứng dụng để đảm bảo toàn bộ dữ liệu được lưu lại một lần nữa."""
        try:
            self.fs.save_to_json()
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu trước khi đóng app: {e}")
        event.accept()