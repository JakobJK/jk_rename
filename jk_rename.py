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


class UI(QtWidgets.QDialog):

    WINDOW_TITLE = "jk_rename"
    qmwInstance = None
    suffix = ['grp', 'joint', 'anim', 'loc', 'crv',
              'ik', 'geo', 'proxyGeo', 'set', 'eff', 'dummy',
              'const', 'Oconst', 'Pconst', 'POconst', 'Aconst'
              ]

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
        self.cwQuickSuffix = self.quickSuffixLayout()
        self.cwSearchAndReplace = self.searchAndReplaceLayout()
        self.cwUtilities = self.utilitiesLayout()

    def renameToolsLayout(self):
        renameToolsWidget = CollapsibleWidget("Rename Tools", True)

        parentLayout = QtWidgets.QVBoxLayout()

        renameLayout = QtWidgets.QHBoxLayout()
        renameLabel = QtWidgets.QLabel('Hash Rename: ')
        renameField = QtWidgets.QLineEdit()
        renameField.setPlaceholderText('exampleName_####_%type%')
        renameLayout.addWidget(renameLabel)
        renameLayout.addWidget(renameField)

        paddingLayout = QtWidgets.QHBoxLayout()
        startLabel = QtWidgets.QLabel('Start #:')
        start = QtWidgets.QLineEdit('1')
        paddingLabel = QtWidgets.QLabel('Padding:')
        padding = QtWidgets.QLineEdit('1')
        paddingLayout.addWidget(startLabel)
        paddingLayout.addWidget(start)
        paddingLayout.addWidget(paddingLabel)
        paddingLayout.addWidget(padding)
        renameButton = QtWidgets.QPushButton('Rename and Number')

        parentLayout.addLayout(renameLayout)
        parentLayout.addLayout(paddingLayout)
        parentLayout.addWidget(renameButton)
        renameToolsWidget.addLayout(parentLayout)
        return renameToolsWidget

    def prefixSuffixLayout(self):
        prefixSuffixWidget = CollapsibleWidget("Prefix - Suffix", True)

        parentLayout = QtWidgets.QVBoxLayout()
        prefixSuffixWidget.addLayout(parentLayout)

        prefixLayout = QtWidgets.QHBoxLayout()
        suffixLayout = QtWidgets.QHBoxLayout()
        parentLayout.addLayout(prefixLayout)
        parentLayout.addLayout(suffixLayout)

        prefixLabel = QtWidgets.QLabel('Prefix: ')
        prefixLabel.setFixedSize(60, 10)

        prefixLineEdit = QtWidgets.QLineEdit()
        prefixButton = QtWidgets.QPushButton('Add')

        prefixLayout.addWidget(prefixLabel)
        prefixLayout.addWidget(prefixLineEdit)
        prefixLayout.addWidget(prefixButton)

        suffixLabel = QtWidgets.QLabel('Suffix: ')
        suffixLabel.setFixedSize(60, 10)

        suffixLineEdit = QtWidgets.QLineEdit()
        suffixButton = QtWidgets.QPushButton('Add')

        suffixLayout.addWidget(suffixLabel)
        suffixLayout.addWidget(suffixLineEdit)
        suffixLayout.addWidget(suffixButton)

        return prefixSuffixWidget

    def quickSuffixLayout(self):
        quickSuffixWidget = CollapsibleWidget("Quick Suffix", False)
        quickSuffixLayout = QtWidgets.QGridLayout()

        for i in range(len(self.suffix)):
            quickSuffixLayout.addWidget(
                QtWidgets.QPushButton(self.suffix[i]),  i - i % 4, i % 4)

        quickSuffixWidget.addLayout(quickSuffixLayout)
        return quickSuffixWidget

    def searchAndReplaceLayout(self):
        searchAndReplaceWidget = CollapsibleWidget("Search and Replace", True)
        parentLayout = QtWidgets.QVBoxLayout()
        searchAndReplaceWidget.addLayout(parentLayout)

        searchLayout = QtWidgets.QHBoxLayout()
        replaceLayout = QtWidgets.QHBoxLayout()
        optionLayout = QtWidgets.QHBoxLayout()
        buttonLayout = QtWidgets.QVBoxLayout()

        buttonLayout.addWidget(QtWidgets.QPushButton('Apply'))
        parentLayout.addLayout(searchLayout)
        parentLayout.addLayout(replaceLayout)
        parentLayout.addLayout(optionLayout)
        parentLayout.addLayout(buttonLayout)

        searchLabel = QtWidgets.QLabel('Search: ')
        searchLabel.setFixedSize(60, 10)
        searchLineEdit = QtWidgets.QLineEdit()

        searchLayout.addWidget(searchLabel)
        searchLayout.addWidget(searchLineEdit)

        replaceLabel = QtWidgets.QLabel('Replace: ')
        replaceLabel.setFixedSize(60, 10)
        replaceLineEdit = QtWidgets.QLineEdit()

        replaceLayout.addWidget(replaceLabel)
        replaceLayout.addWidget(replaceLineEdit)

        optionLayout.addStretch()
        optionLayout.addWidget(QtWidgets.QRadioButton('Hierachy'))
        optionLayout.addStretch()
        optionLayout.addWidget(QtWidgets.QRadioButton('Selected'))
        optionLayout.addStretch()
        optionLayout.addWidget(QtWidgets.QRadioButton('All'))
        optionLayout.addStretch()

        return searchAndReplaceWidget

    def searchAndReplaceState(self):
        pass

    def utilitiesLayout(self):
        utilitiesWidget = CollapsibleWidget("Utilities", True)
        parentLayout = QtWidgets.QVBoxLayout()
        parentLayout.addWidget(QtWidgets.QPushButton('Rename Shapes'))
        parentLayout.addWidget(
            QtWidgets.QPushButton('Selected Duplicated Names'))
        utilitiesWidget.addLayout(parentLayout)

        return utilitiesWidget

    def create_layout(self):
        self.bodyWidget = QtWidgets.QWidget()
        self.bodyLayout = QtWidgets.QVBoxLayout(self.bodyWidget)
        self.bodyLayout.setContentsMargins(4, 2, 4, 2)
        self.bodyLayout.setSpacing(3)
        self.bodyLayout.setAlignment(QtCore.Qt.AlignTop)

        self.bodyLayout.addWidget(self.cwRenameTools)
        self.bodyLayout.addWidget(self.cwPrefixSuffix)
        self.bodyLayout.addWidget(self.cwQuickSuffix)
        self.bodyLayout.addWidget(self.cwSearchAndReplace)
        self.bodyLayout.addWidget(self.cwUtilities)

        self.bodyScrollArea = QtWidgets.QScrollArea()
        self.bodyScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.bodyScrollArea.setWidgetResizable(True)
        self.bodyScrollArea.setWidget(self.bodyWidget)

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.bodyScrollArea)


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
        self.setExpanded(True)

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

    def __init__(self, text, expanded=False, parent=None):
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

        self.setExpanded(expanded)

    def addWidget(self, widget):
        self.bodyLayout.addWidget(widget)

    def addLayout(self, layout):
        self.bodyLayout.addLayout(layout)

    def setExpanded(self, expanded):
        self.header.setExpanded(expanded)
        self.body.setVisible(expanded)

    def onHeaderClicked(self):
        self.setExpanded(not self.header.isExpanded())


if __name__ == '__main__':
    try:
        win.close()
    except:
        pass
    win = UI(parent=getMainWindow())
    win.show()
    win.raise_()
