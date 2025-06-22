"""
    jk_rename v.0.1.0
    A renamer for Autodesk Maya inspired by WP_Rename by William Petruccelli
    Contact: jakobjk@gmail.com
    https://github.com/JakobJK/jk_rename
"""
from typing import List
from enum import Enum

import maya.cmds as cmds


# Renamer Enums classes
class SearchAndReplaceState(str, Enum):
    """State for search and replace functionality."""

    HIERARCHY = 'hierarchy'
    SELECTED = 'selected'
    ALL = 'all'


class AffixType(str, Enum):
    """AffixType for the renamers 'add suffix' and 'add prefix' functions"""

    SUFFIX = 'suffix'
    PREFIX = 'prefix'


class CharacterRemovalPosition(str, Enum):
    """Type to for the renamers remove character functionality."""

    FIRST = 'first'
    LAST = 'last'


def add_affix(affix: str, affix_type: AffixType):
    """
    Adds a prefix or suffix to selected objects' names in Maya based on the given affix type.

    Args:
        affix (str): The string to add as a prefix or suffix.
        affix_type (AffixType): The type of affix to add, can be either AffixType.PREFIX or AffixType.SUFFIX.
    """

    selected_uuids = cmds.ls(sl=True, uuid=True)

    for obj_uuid in selected_uuids:
        full_obj_name = cmds.ls(obj_uuid, long=True)[0]
        object_name = full_obj_name.split('|')[-1]
        new_name = affix + object_name if affix_type == 'prefix' else object_name + affix
        try:
            cmds.rename(full_obj_name, new_name)
        except Exception as e:
            print(f'Error renaming {full_obj_name}: {e}')


def search_and_replace(state: SearchAndReplaceState, search_string: str, replace_string: str):
    """
    Searches for and replaces part of the names of nodes based on the specified state.

    This function reads the user-specified search and replace texts, iterates through nodes based on the state
    provided (either 'hierarchy', 'selected', or 'all'), and renames nodes by replacing occurrences of the
    search text with the replace text in each node's name.

    Args:
        state (SearchAndReplaceState): The state that determines which nodes to operate on.
            - SearchAndReplaceState.HIERARCHY: Operates on all nodes in the hierarchy of the selected objects.
            - SearchAndReplaceState.SELECTED: Operates only on currently selected nodes.
            - SearchAndReplaceState.ALL: Operates on all nodes.
        search_string (str): The text to search for within the node names.
        replace_string (str): The text to use for replacing the search string.
    """
    uuids = _get_nodes(state)

    for uuid in uuids:
        full_name = cmds.ls(uuid, uuid=True)[0]
        short_name = full_name.split('|')[-1]
        if search_string in short_name:
            new_name = short_name.replace(search_string, replace_string)
            try:
                cmds.rename(full_name, new_name)
            except Exception as e:
                print(f'Error renaming {full_name}: {e}')


def _get_nodes(state: SearchAndReplaceState) -> List[str]:
    """
    Retrieves nodes based on the specified state and returns their UUIDs.

    Args:
        state (SearchAndReplaceState): The state determining which nodes to retrieve. This can be one of three options:
            - SearchAndReplaceState.HIERARCHY
            - SearchAndReplaceState.SELECTED
            - SearchAndReplaceState.ALL
    """
    if state == SearchAndReplaceState.HIERARCHY:
        selected = cmds.ls(selection=True, long=True)
        all_nodes = set()

        for obj in selected:
            all_nodes.add(cmds.ls(obj, uuid=True)[0])
            descendants = cmds.listRelatives(obj, allDescendents=True, fullPath=True) or []
            for descendant in descendants:
                all_nodes.add(cmds.ls(descendant, uuid=True)[0])

    elif state == SearchAndReplaceState.SELECTED:
        all_nodes = {cmds.ls(obj, uuid=True)[0] for obj in cmds.ls(selection=True, long=True)}

    elif state == SearchAndReplaceState.ALL:
        all_nodes = {cmds.ls(obj, uuid=True)[0] for obj in cmds.ls(type="transform", long=True)}

    else:
        all_nodes = set()

    return list(all_nodes)


def select_duplicated_names():
    """
    Selects nodes in the current Maya scene that have duplicated names.
    """
    duplicated_names = [node for node in cmds.ls(transforms=True) if '|' in node]
    if len(duplicated_names) == 0:
        print('No Duplicated Names.')
    else:
        cmds.select(duplicated_names)


def remove_character(position: CharacterRemovalPosition):
    """
    Removes the first or last character from the names of selected objects in Maya.

    Args:
        position (CharacterRemovalPosition): Specifies whether to remove the 'first' or 'last' character
        from each selected object's name. It must be one of:
            - CharacterRemovalPosition.FIRST: to remove the first character.
            - CharacterRemovalPosition.LAST: to remove the last character.
    """
    selection = cmds.ls(selection=True, uuid=True)

    for obj_uuid in selection:
        full_name = cmds.ls(obj_uuid, long=True)[0]
        short_name = full_name.split('|')[-1]

        if position == CharacterRemovalPosition.FIRST and len(short_name) > 1:
            new_name = short_name[1:]
        elif position == CharacterRemovalPosition.LAST and len(short_name) > 1:
            new_name = short_name[:-1]
        else:
            continue

        try:
            cmds.rename(full_name, new_name)
        except Exception as e:
            print.warning(f'Error renaming object with UUID {obj_uuid}: {e}')


def hash_rename(new_name: str):
    """
    Renames selected objects in Maya by sequentially numbering them, using '#' in `new_name` as placeholders for digits.

    The function expects `new_name` to contain hash characters ('#') which are placeholders for numerical increments.
    If `new_name` does not contain any '#', one is appended at the end. The function then checks for the validity
    of the hash block (consecutive '#' characters). If the hash block is valid, it renames each selected object by
    replacing the hash block with a zero-padded number corresponding to the object's index in the selection order.
    If the hash block is invalid (non-consecutive '#' or other issues), a warning is issued and no renaming occurs.

    Args:
        new_name (str): The base name pattern to apply, which should include one or more consecutive '#' characters
        to indicate where numeric padding should be applied.
    """

    if '#' not in new_name:
        new_name += '#'

    if not _validate_hash_block(new_name):
        return cmds.warning('Invalid hash block')

    amount_of_hashes = new_name.count('#')
    selection = cmds.ls(selection=True, uuid=True)

    for idx, obj_uuid in enumerate(selection):
        padding = str(idx + 1).rjust(amount_of_hashes, '0')
        to_name = new_name.replace('#' * amount_of_hashes, padding)
        current_name = cmds.ls(obj_uuid, long=True)[0]
        cmds.rename(current_name, to_name)


def _validate_hash_block(new_name: str) -> bool:
    """
    Validates if the hash ('#') characters in `new_name` are consecutive.

    Args:
        new_name (str): The name string to validate for consecutive hash marks.

    Returns:
        bool: True if all the hashes are consecutive and form a single uninterrupted block, False otherwise.
    """
    amount_of_hashes = new_name.count('#')
    return amount_of_hashes * '#' in new_name


def rename_shapes():
    """
    Renames shape nodes to follow their parent transform node's name with a "Shape" suffix.
    """
    transform_nodes = cmds.ls(type="transform", long=True)
    default_nodes = {"|top", "|front", "|side"}
    renamed_nodes = 0
    for transform_node in transform_nodes:
        if transform_node in default_nodes:
            continue

        shape_nodes = cmds.listRelatives(transform_node, shapes=True, fullPath=True) or []
        new_shape_name = transform_node.split('|')[-1] + "Shape"
        for shape_node in shape_nodes:
            current_shape_name = shape_node.split('|')[-1]
            if current_shape_name == new_shape_name:
                continue
            try:
                cmds.rename(shape_node, new_shape_name)
                renamed_nodes += 1
            except Exception as e:
                print(f"Error renaming shape node {shape_node}: {e}")
    print(f"Renamed {renamed_nodes} shape node{'' if renamed_nodes == 1 else 's'}.")
