from typing import Literal

from PySide6 import QtCore, QtWidgets
import maya.OpenMayaUI as omui
from shiboken6 import wrapInstance

from jk_rename.rename import (
    add_affix,
    hash_rename,
    remove_character,
    rename_shapes,
    search_and_replace,
    select_duplicated_names,
    AffixType,
    CharacterRemovalPosition,
    SearchAndReplaceState
)

def get_main_maya_window():
    mainWindowPtr = omui.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(int(mainWindowPtr), QtWidgets.QWidget)
    return mayaMainWindow

class RenamerUI(QtWidgets.QMainWindow):
    """
    Renamer of Maya DAG nodes.
    """

    qmwInstance = None
    
    @classmethod
    def show_UI(cls):
        if not cls.qmwInstance:
            cls.qmwInstance = RenamerUI()
        if cls.qmwInstance.isHidden():
            cls.qmwInstance.show()
        else:
            cls.qmwInstance.raise_()
        
        cls.qmwInstance.activateWindow()

    def __init__(self, parent: QtWidgets.QWidget = get_main_maya_window(), **kwargs):
        """Initializer.

        Args:
            **kwargs: Key woard arguments are passed to the menu constructor to
                further configure the menu.
        """
        super().__init__(**kwargs)

        self.setWindowFlags(
            QtCore.Qt.Tool |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowSystemMenuHint
        )
        self.setWindowTitle("JK Rename")
        self._create_layout()
        self._create_widgets()

    def _create_widgets(self):
        """
        Creates and add all the widgets to main rename layout
        """
        self._build_rename_tools()
        self._build_affix_()
        self._build_search_and_replace()
        self._build_utilities()

    def _create_layout(self):
        """
        Creates the main layout of the Renamer UI
        """
        self.body_widget = QtWidgets.QWidget()
        self.body_layout = QtWidgets.QVBoxLayout(self.body_widget)
        self.body_layout.setContentsMargins(4, 2, 4, 2)
        self.body_layout.setSpacing(3)
        self.body_layout.setAlignment(QtCore.Qt.AlignTop)

        self.bodyScrollArea = QtWidgets.QScrollArea()
        self.bodyScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.bodyScrollArea.setWidgetResizable(True)
        self.bodyScrollArea.setWidget(self.body_widget)

        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.bodyScrollArea)

        self.setCentralWidget(central_widget)

    def _build_rename_tools(self):
        """
        Build the Rename Tools UI Widget
        """
        rename_tools_widget = QtWidgets.QGroupBox("Rename Tools")
        parent_layout = QtWidgets.QVBoxLayout()

        rename_layout = QtWidgets.QHBoxLayout()
        rename_label = QtWidgets.QLabel('Hash Rename: ')
        rename_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        rename_label.setFixedWidth(130)

        self.rename_field = QtWidgets.QLineEdit()
        self.rename_field.setPlaceholderText('example_####_geo')

        rename_layout.addWidget(rename_label)
        rename_layout.addWidget(self.rename_field)

        rename_button = QtWidgets.QPushButton('Rename and Number')
        rename_button.clicked.connect(lambda: hash_rename(self.rename_field.text()))

        parent_layout.addLayout(rename_layout)
        parent_layout.addWidget(rename_button)

        rename_tools_widget.setLayout(parent_layout)
        self.body_layout.addWidget(rename_tools_widget)

    def _build_affix_(self):
        """
        Build the Prefix - Suffix UI Widget
        """
        affix_widget = QtWidgets.QGroupBox("Prefix - Suffix")

        parent_layout = QtWidgets.QVBoxLayout()
        prefix_layout = QtWidgets.QHBoxLayout()
        suffix_layout = QtWidgets.QHBoxLayout()

        parent_layout.addLayout(prefix_layout)
        parent_layout.addLayout(suffix_layout)

        prefix_label = QtWidgets.QLabel('Prefix: ')
        prefix_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        prefix_label.setFixedWidth(130)
        self.prefix_line_edit = QtWidgets.QLineEdit()
        prefix_button = QtWidgets.QPushButton('Add')
        prefix_button.clicked.connect(lambda: add_affix(self.prefix_line_edit.text(), affix_type=AffixType.PREFIX))

        prefix_layout.addWidget(prefix_label)
        prefix_layout.addWidget(self.prefix_line_edit)
        prefix_layout.addWidget(prefix_button)

        suffix_label = QtWidgets.QLabel('Suffix: ')
        suffix_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        suffix_label.setFixedWidth(130)
        self.suffix_line_edit = QtWidgets.QLineEdit()
        suffix_button = QtWidgets.QPushButton('Add')
        suffix_button.clicked.connect(lambda: add_affix(self.suffix_line_edit.text(), affix_type=AffixType.SUFFIX))

        suffix_layout.addWidget(suffix_label)
        suffix_layout.addWidget(self.suffix_line_edit)
        suffix_layout.addWidget(suffix_button)

        affix_widget.setLayout(parent_layout)

        self.body_layout.addWidget(affix_widget)

    def _build_search_and_replace(self):
        """
        Build the search and replace UI Widget
        """
        search_and_replace_widget = QtWidgets.QGroupBox("Search and Replace")
        parent_layout = QtWidgets.QVBoxLayout()

        search_layout = QtWidgets.QHBoxLayout()
        search_label = QtWidgets.QLabel('Search: ')
        search_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        search_label.setFixedSize(130, 20)
        self.search_line_edit = QtWidgets.QLineEdit()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_line_edit)

        replace_layout = QtWidgets.QHBoxLayout()
        replace_label = QtWidgets.QLabel('Replace: ')
        replace_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        replace_label.setFixedSize(130, 20)
        self.replace_line_edit = QtWidgets.QLineEdit()
        replace_layout.addWidget(replace_label)
        replace_layout.addWidget(self.replace_line_edit)

        option_layout = QtWidgets.QHBoxLayout()
        self.radio_group = QtWidgets.QButtonGroup(search_and_replace_widget)
        hierarchy_btn = QtWidgets.QRadioButton('Hierarchy')
        selected_btn = QtWidgets.QRadioButton('Selected')
        all_btn = QtWidgets.QRadioButton('All')
        selected_btn.setChecked(True)
        self.radio_group.addButton(hierarchy_btn)
        self.radio_group.addButton(selected_btn)
        self.radio_group.addButton(all_btn)
        option_layout.addStretch(1)
        option_layout.addWidget(hierarchy_btn)
        option_layout.addStretch(1)
        option_layout.addWidget(selected_btn)
        option_layout.addStretch(1)
        option_layout.addWidget(all_btn)
        option_layout.addStretch(1)

        button_layout = QtWidgets.QVBoxLayout()
        search_and_replace_btn = QtWidgets.QPushButton('Apply')
        search_and_replace_btn.clicked.connect(self.run_search_and_replace)
        button_layout.addWidget(search_and_replace_btn)

        parent_layout.addLayout(search_layout)
        parent_layout.addLayout(replace_layout)
        parent_layout.addLayout(option_layout)
        parent_layout.addLayout(button_layout)

        search_and_replace_widget.setLayout(parent_layout)

        self.body_layout.addWidget(search_and_replace_widget)

    def _build_utilities(self):
        """
        Build the utilities UI Widget
        """
        utilities_widget = QtWidgets.QGroupBox("Utilities")
        parent_layout = QtWidgets.QVBoxLayout()

        remove_first_char_btn = QtWidgets.QPushButton('Remove First Character')
        remove_first_char_btn.clicked.connect(lambda: remove_character(CharacterRemovalPosition.FIRST))

        remove_last_char_btn = QtWidgets.QPushButton('Remove Last Character')
        remove_last_char_btn.clicked.connect(lambda: remove_character(CharacterRemovalPosition.LAST))

        remove_char_layout = QtWidgets.QHBoxLayout()
        remove_char_layout.addWidget(remove_first_char_btn)
        remove_char_layout.addWidget(remove_last_char_btn)

        parent_layout.addLayout(remove_char_layout)

        rename_shapes_btn = QtWidgets.QPushButton('Rename All Shapes')
        rename_shapes_btn.clicked.connect(rename_shapes)
        parent_layout.addWidget(rename_shapes_btn)

        sel_duplicated_names_btn = QtWidgets.QPushButton('Select Duplicated Names')
        sel_duplicated_names_btn.clicked.connect(select_duplicated_names)
        parent_layout.addWidget(sel_duplicated_names_btn)

        utilities_widget.setLayout(parent_layout)
        self.body_layout.addWidget(utilities_widget)

    def run_search_and_replace(self):
        """Executes a search and replace operation based on the UI state."""
        state = self._get_checked_state(self.radio_group)
        search_string = self.search_line_edit.text()
        replace_string = self.replace_line_edit.text()
        search_and_replace(state, search_string, replace_string)

    def _get_checked_state(self, button_group: QtWidgets.QButtonGroup) -> SearchAndReplaceState:
        """Retrieves the checked radio button in a QButtonGroup and returns its label in lowercase.

        Args:
            button_group (QtWidgets.QButtonGroup): The group of radio buttons to check.

        Returns:
            str: The text of the checked radio button in lowercase, or an empty string if none are checked.
        """
        for button in button_group.buttons():
            if button.isChecked():
                button_text = button.text().lower()
                return SearchAndReplaceState(button_text)
        return SearchAndReplaceState.SELECTED
