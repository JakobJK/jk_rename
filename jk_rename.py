"""
    jk_rename v.0.1.0
    A renamer for Autodesk Maya inspired by wp_rename by William Petruccelli
    Contact: jakobjk@gmail.com
    https://github.com/JakobJK/jk_rename
"""

from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui


def getMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    mainWindow = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return mainWindow


class CollapsibleHeader(QtWidgets.QWidget):

    COLLAPSED_PIXMAP = QtGui.QPixmap(":teRightArrow.png")
    EXPANDED_PIXMAP = QtGui.QPixmap(":teDownArrow.png")

    clicked = QtCore.Signal()

    def __init__(self, text, parent=None):
        super(CollapsibleHeader, self).__init__(parent)

        self.setAutoFillBackground(True)

        self.iconLabel = QtWidgets.QLabel()
        self.iconLabel.setFixedWidth(self.COLLAPSED_PIXMAP.width())
        textLabel = QtWidgets.QLabel()
        textLabel.setText("<b>{0}</b>".format(text))
        textLabel.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.setContentsMargins(4, 4, 4, 4)
        self.mainLayout.addWidget(self.iconLabel)
        self.mainLayout.addWidget(textLabel)

        palette = self.palette()
        color = QtGui.QColor.fromRgbF(0.364706, 0.364706, 0.364706, 1.000000)
        palette.setColor(QtGui.QPalette.Window, color)
        self.setPalette(palette)
        self.setExpanded(False)

    def isExpanded(self):
        return self.expanded

    def setExpanded(self, _expanded):
        self.expanded = _expanded

        if(self.expanded):
            self.iconLabel.setPixmap(self.EXPANDED_PIXMAP)
        else:
            self.iconLabel.setPixmap(self.COLLAPSED_PIXMAP)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()


class CollapsibleWidget(QtWidgets.QWidget):

    def __init__(self, text, parent=None):
        super(CollapsibleWidget, self).__init__(parent)

        self.header = CollapsibleHeader(text)
        self.header.clicked.connect(
            self.onHeaderClicked)

        self.body = QtWidgets.QWidget()

        self.bodyLayout = QtWidgets.QVBoxLayout(self.body)
        self.bodyLayout.setContentsMargins(4, 2, 4, 2)
        self.bodyLayout.setSpacing(3)

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.header)
        self.mainLayout.addWidget(self.body)

        self.setExpanded(False)

    def addWidget(self, widget):
        self.bodyLayout.addWidget(widget)

    def addLayout(self, layout):
        self.bodyLayout.addLayout(layout)

    def setExpanded(self, expanded):
        self.header.setExpanded(expanded)
        self.body.setVisible(expanded)

    def onHeaderClicked(self):
        self.setExpanded(not self.header.isExpanded())


class UI(QtWidgets.QDialog):

    WINDOW_TITLE = "jk_rename"
    qmwInstance = None

    @classmethod
    def show_UI(cls):
        if not cls.qmwInstance:
            cls.qmwInstance = UI()
        if cls.qmwInstance.isHidden():
            cls.qmwInstance.show()
        else:
            cls.qmwInstance.raise_()
            cls.qmwInstance.activateWindow()

    def __init__(self, parent=getMainWindow()):
        super(UI, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^
                                QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        self.cwRenameTools = self.renameToolsLayout()
        self.cwPrefixSuffix = self.prefixSuffixLayout()
        self.cwSearchAndReplace = self.searchAndReplaceLayout()
        self.cwUtilities = self.utilitiesLayout()

    def renameToolsLayout(self):
        return CollapsibleWidget("Rename Tools")

    def prefixSuffixLayout(self):
        return CollapsibleWidget("Prefix - Suffix")

    def searchAndReplaceLayout(self):
        return CollapsibleWidget("Search and Replace")

    def utilitiesLayout(self):
        return CollapsibleWidget("Utilities")

    def create_layout(self):
        self.bodyWidget = QtWidgets.QWidget()

        self.bodyLayout = QtWidgets.QVBoxLayout(self.bodyWidget)
        self.bodyLayout.setContentsMargins(4, 2, 4, 2)
        self.bodyLayout.setSpacing(3)
        self.bodyLayout.setAlignment(QtCore.Qt.AlignTop)

        self.bodyLayout.addWidget(self.cwRenameTools)
        self.bodyLayout.addWidget(self.cwPrefixSuffix)
        self.bodyLayout.addWidget(self.cwSearchAndReplace)
        self.bodyLayout.addWidget(self.cwUtilities)

        self.bodyScrollArea = QtWidgets.QScrollArea()
        self.bodyScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.bodyScrollArea.setWidgetResizable(True)
        self.bodyScrollArea.setWidget(self.bodyWidget)

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.bodyScrollArea)


if __name__ == '__main__':
    try:
        win.close()
    except:
        pass
    win = UI(parent=getMainWindow())
    win.show()
    win.raise_()
