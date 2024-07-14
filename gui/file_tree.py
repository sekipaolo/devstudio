import logging
from PyQt6.QtWidgets import QTreeView, QStyledItemDelegate, QStyle, QStyleOptionViewItem
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt6.QtCore import Qt, QRect

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class FileTreeItem(QStandardItem):
    def __init__(self, text, is_dir=False):
        super().__init__(text)
        self.setCheckable(True)
        self.is_dir = is_dir
        self.setCheckState(Qt.CheckState.Unchecked)
        logging.debug(f"Created FileTreeItem: {text}, is_dir: {is_dir}")

    def __lt__(self, other):
        if self.is_dir and not other.is_dir:
            return True
        elif not self.is_dir and other.is_dir:
            return False
        return self.text().lower() < other.text().lower()

class FileTreeModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        logging.debug("FileTreeModel initialized")

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        result = super().setData(index, value, role)
        if role == Qt.ItemDataRole.CheckStateRole:
            item = self.itemFromIndex(index)
            logging.debug(f"Check state changed for {item.text()}: {value}")
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
        return result

class FileTreeDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()
        
        # Draw background
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        else:
            painter.fillRect(option.rect, QColor(35, 35, 35))

        # Draw checkbox
        check_rect = self.getCheckboxRect(option)
        self.drawCheck(painter, option, check_rect, self.getCheckState(index))

        # Draw text
        text_rect = option.rect.adjusted(check_rect.width() + 5, 0, 0, 0)
        text_color = QColor(255, 255, 255) if option.state & QStyle.StateFlag.State_Selected else QColor(200, 200, 200)
        painter.setPen(text_color)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, index.data())

        painter.restore()

    def getCheckboxRect(self, option):
        return QRect(option.rect.x() + 2, option.rect.y() + 2, option.rect.height() - 4, option.rect.height() - 4)

    def getCheckState(self, index):
        return index.data(Qt.ItemDataRole.CheckStateRole)

    def drawCheck(self, painter, option, rect, state):
        if state == Qt.CheckState.Checked:
            painter.fillRect(rect, QColor(0, 120, 215))
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "✓")
        elif state == Qt.CheckState.PartiallyChecked:
            painter.fillRect(rect, QColor(0, 120, 215))
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "-")
        else:
            painter.setPen(QColor(150, 150, 150))
            painter.drawRect(rect)

class FileTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(FileTreeModel(self))
        self.setHeaderHidden(True)
        self.setItemDelegate(FileTreeDelegate())
        self.setSortingEnabled(True)
        self.setStyleSheet("""
            QTreeView {
                background-color: #232323;
                color: #FFFFFF;
            }
            QTreeView::item:selected {
                background-color: #353535;
            }
        """)
        self.clicked.connect(self.on_item_clicked)
        logging.debug("FileTreeView initialized")

    def on_item_clicked(self, index):
        item = self.model().itemFromIndex(index)
        rect = self.visualRect(index)
        option = QStyleOptionViewItem()
        option.rect = rect
        check_rect = self.itemDelegate().getCheckboxRect(option)
        
        logging.debug(f"Item clicked: {item.text()}, Is directory: {getattr(item, 'is_dir', False)}")
        logging.debug(f"Click position: {self.mapFromGlobal(self.cursor().pos())}")
        logging.debug(f"Check rect: {check_rect}")
        
        if check_rect.contains(self.mapFromGlobal(self.cursor().pos())):
            logging.debug("Click was on checkbox")
            self.toggle_check_state(index)
        else:
            logging.debug("Click was not on checkbox")

    def toggle_check_state(self, index):
        item = self.model().itemFromIndex(index)
        logging.debug(f"Toggling check state for {item.text()}")
        logging.debug(f"Current state: {item.checkState()}")
        new_state = Qt.CheckState.Unchecked if item.checkState() == Qt.CheckState.Checked else Qt.CheckState.Checked
        logging.debug(f"New state: {new_state}")
        self.model().setData(index, new_state, Qt.ItemDataRole.CheckStateRole)
        self.update(index)
        logging.debug(f"State after toggle: {item.checkState()}")

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid():
            rect = self.visualRect(index)
            option = QStyleOptionViewItem()
            option.rect = rect
            check_rect = self.itemDelegate().getCheckboxRect(option)
            if check_rect.contains(event.pos()):
                self.on_item_clicked(index)
                return
        super().mousePressEvent(event)

    def set_check_state_recursive(self, item, state):
        logging.debug(f"Setting check state for {item.text()}")
        logging.debug(f"Current state: {item.checkState()}")
        item.setCheckState(state)
        logging.debug(f"State after set: {item.checkState()}")
        
        if item.is_dir:
            for row in range(item.rowCount()):
                child = item.child(row)
                self.set_check_state_recursive(child, state)

    def update_parent_check_states(self, parent):
        if not parent:
            return

        checked_count = 0
        total_count = 0
        for row in range(parent.rowCount()):
            child = parent.child(row)
            if child.checkState() == Qt.CheckState.Checked:
                checked_count += 1
            elif child.checkState() == Qt.CheckState.PartiallyChecked:
                parent.setCheckState(Qt.CheckState.PartiallyChecked)
                self.update_parent_check_states(parent.parent())
                return
            total_count += 1

        logging.debug(f"Updating parent {parent.text()}: {checked_count}/{total_count} checked")
        logging.debug(f"Current parent state: {parent.checkState()}")

        if checked_count == 0:
            parent.setCheckState(Qt.CheckState.Unchecked)
        elif checked_count == total_count:
            parent.setCheckState(Qt.CheckState.Checked)
        else:
            parent.setCheckState(Qt.CheckState.PartiallyChecked)

        logging.debug(f"New parent state: {parent.checkState()}")

        self.update_parent_check_states(parent.parent())