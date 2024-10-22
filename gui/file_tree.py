import os
from PyQt6.QtWidgets import QTreeView, QStyle, QProxyStyle, QStyleOptionViewItem
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPalette, QPainter, QPen
from PyQt6.QtCore import Qt, QRect
from typing import List, Dict

class CheckboxStyle(QProxyStyle):
    def subElementRect(self, element, option, widget=None):
        r = super().subElementRect(element, option, widget)
        if element == QStyle.SubElement.SE_ItemViewItemCheckIndicator:
            r.moveLeft(option.rect.left() + 3)  # Move checkbox to the left
            r.moveCenter(QRect(r.left(), option.rect.center().y(), r.width(), r.height()).center())
        return r

    def drawPrimitive(self, element, option, painter, widget=None):
        if element == QStyle.PrimitiveElement.PE_IndicatorItemViewItemCheck:
            # Draw white border around the checkbox
            painter.save()
            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            painter.drawRect(option.rect.adjusted(0, 0, -1, -1))
            painter.restore()
        super().drawPrimitive(element, option, painter, widget)

class FileTreeView(QTreeView):
    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.clicked.connect(self.on_item_clicked)
        self.doubleClicked.connect(self.on_item_double_clicked)
        
        # Apply custom style to make checkboxes visible in dark mode
        self.setStyle(CheckboxStyle(self.style()))

    def populate(self, root_path):
        self.model.clear()
        root_item = self.model.invisibleRootItem()
        self._populate_recursive(root_path, root_item)

    def _populate_recursive(self, directory: str, parent: QStandardItem):
        for name in sorted(os.listdir(directory)):
            if name in ['.git', '__pycache__', 'history']:
                continue
            path = os.path.join(directory, name)
            item = QStandardItem(name)
            item.setCheckable(True)
            item.setData(path, Qt.ItemDataRole.UserRole)
            parent.appendRow(item)
            if os.path.isdir(path):
                item.setData(True, Qt.ItemDataRole.UserRole + 1)  # Store is_dir information
                self._populate_recursive(path, item)
            else:
                item.setData(False, Qt.ItemDataRole.UserRole + 1)

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid():
            rect = self.visualRect(index)
            checkbox_rect = self.style().subElementRect(QStyle.SubElement.SE_ItemViewItemCheckIndicator, 
                                                        QStyleOptionViewItem(), self)
            checkbox_rect.moveTopLeft(rect.topLeft())
            if checkbox_rect.contains(event.pos()):
                item = self.model.itemFromIndex(index)
                item.setCheckState(Qt.CheckState.Checked if item.checkState() == Qt.CheckState.Unchecked else Qt.CheckState.Unchecked)
                event.accept()
                return
        super().mousePressEvent(event)

    def on_item_clicked(self, index):
        # This method is now only for selection, not for checkbox toggling
        pass

    def on_item_double_clicked(self, index):
        item = self.model.itemFromIndex(index)
        if not item.data(Qt.ItemDataRole.UserRole + 1):  # Not a directory
            # Implement rename functionality here
            pass

    def get_selected_files(self) -> List[Dict[str, str]]:
        selected_files = []
        def traverse(parent: QStandardItem):
            for row in range(parent.rowCount()):
                child = parent.child(row)
                if child.checkState() == Qt.CheckState.Checked and not child.data(Qt.ItemDataRole.UserRole + 1):
                    file_path = child.data(Qt.ItemDataRole.UserRole)
                    try:
                        with open(file_path, 'r') as file:
                            content = file.read()
                        selected_files.append({"path": file_path, "content": content})
                    except Exception as e:
                        print(f"Error reading file {file_path}: {str(e)}")
                if child.hasChildren():
                    traverse(child)
        
        root = self.model.invisibleRootItem()
        traverse(root)
        return selected_files

    def get_file_path(self, item: QStandardItem) -> str:
        path = []
        while item is not None:
            path.append(item.text())
            item = item.parent()
        return os.path.join(*reversed(path[:-1]))  # Exclude the invisible root item
