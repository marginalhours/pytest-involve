# -*- coding: utf-8 -*-
"""
This module contains the implementation of the pytest_involve plugin. It
is just about small enough to be implemented in a single *.py file, split
into the following four regions with #region / #endRegion:

* imports
* pytest hooks -- Functions the pytest framework will call
* data structures -- the definition of the ImportSet class
* plugin code -- core plugin functionality

"""
# region imports

import sys
from collections.abc import Hashable
from functools import lru_cache
from importlib import import_module
from inspect import ismodule
from pathlib import Path
from types import ModuleType
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

# endregion

# region pytest hooks


def pytest_addoption(parser):
    """Add the --involving command line argument to the pytest argument
    parser via the pytest_addoption hook. We use action=append so that this
    flag can be passed multiple times to build up a list of files to cover"""
    group = parser.getgroup("involve")
    group.addoption(
        "--involving",
        action="append",
        help=(
            "Python source files, folders, modules, "
            "or module members to find tests involving"
        ),
    )


def pytest_report_header(config):
    """Add the files being covered to the pytest preamble, via the
    pytest_report_header hook"""
    involved_objects = get_involved_objects(config)

    if involved_objects:
        return [
            "Running tests involving:",
            *[f"    {involved}" for involved in sorted(involved_objects)],
        ]

    return []


def pytest_pycollect_makeitem(collector, name, obj):
    """Don't collect from modules that don't import any relevant files"""
    involved_files_and_members = get_involved_files_and_members(collector.config)

    if involved_files_and_members:
        if should_module_be_included(collector.module, involved_files_and_members):
            return None
        else:
            return []

    return None


# endregion

# region datastructures


class ImportSet:
    """A utility class for holding which members from a module have been
    imported into a file, plus if the module itself has been. This class
    is used in two ways:

    - For collecting the relevant files and members specified using --involving
    - For collecting the imports in a module.

    Once both have been done, comparing the two to see if any relevant things
    are imported into a module is much simpler.
    """

    def __init__(self, module_file, has_full_import, imported_members=None):
        """Constructor

        Arguments:
            module_file (ModuleType): The file where a module is defined
            has_full_import (bool): Whether or not the module is imported
                                    completely into the module this ImportSet
                                    belongs to
        Keyword Arguments:
            imported_members (Set[str]): Set of members imported into the module
                                        (default: set())
        """
        self.module_file = module_file
        self.has_full_import = has_full_import
        self.imported_members = imported_members or set()

    def __hash__(self):
        """Hash implementation to use with @lru_cache"""
        return hash(
            (self.module_file, self.has_full_import, frozenset(self.imported_members))
        )

    def __eq__(self, other):
        """Equality implementation mostly used for testing"""
        if not isinstance(other, ImportSet):
            return False
        if not self.module_file == other.module_file:
            return False
        elif self.has_full_import != other.has_full_import:
            return False
        else:
            return self.imported_members == other.imported_members

    def __repr__(self):
        """The __repr__ of an ImportSet is a string that allows it to be
        reconstructed completely"""
        return (
            f"ImportSet('{self.module_file}', "
            f"{self.has_full_import}, {self.imported_members})"
        )

    def __str__(self):
        """The __str__ of an ImportSet is a string that indicates the module file,
        whether it's fully imported or not, and then a list of its members."""
        module_status_string = "✓" if self.has_full_import else "✗"
        return (
            f"<ImportSet "
            f"{self.module_file} [{module_status_string}] "
            f"-- {self.imported_members} >"
        )


# endregion

# region plugin code


@lru_cache()
def get_involved_objects(config):
    """Given a pytest config, get the list of objects specified via the
    --involving flag"""
    return config.getoption("--involving") or []


@lru_cache()
def get_involved_files_and_members(config) -> Dict[str, Set[str]]:
    """Given a pytest config, return the set of files specified by the
    --involving flag

    Args:
        config: pytest config object

    Returns:
        Dict[str, Set[str]]: Output of build_involved_files_and_members
    """
    return build_involved_files_and_members(get_involved_objects(config))


@lru_cache()
def should_module_be_included(
    module: ModuleType, involved_filter: FrozenSet[Tuple[str, FrozenSet[str]]]
):
    """Given a Python module and a dictionary filter object of files and members
    specified with the --involving flag, decide if tests from the module
    should be included in the pytest run.

    Arguments:
        module (ModuleType): The module about which a decision should be made
        involved_filter (Dict[str, Set[str]]): The filter of involved files
                                                 and members to check if the
                                                 module imports
    Returns:
        Optional[List]: The empty list to avoid collecting test from the module,
                        or None to return control to pytest.
    """
    imported_files_and_members = get_members_by_file(module.__dict__)
    imported_files = set(imported_files_and_members.keys())

    involved_files_and_members = dict(involved_filter)
    involved_files = set(involved_files_and_members.keys())

    intersecting_files = imported_files & involved_files

    if not intersecting_files:
        # If there no files specified with --involving which are imported
        # into this module, return False.
        return False
    else:
        for file_name in intersecting_files:
            imported_set = imported_files_and_members[file_name]
            involved_set = involved_files_and_members[file_name]

            if imported_set.has_full_import or involved_set.has_full_import:
                # If either set has a full import, return True.
                # This deals with 2 cases:
                #
                # (1) involved module, imported member
                # (2) involved member, imported module
                #
                # In either case there is a possibility that the module
                # contains a relevant test, and recall is more important than
                # precision.
                return True

            imported_file_members = imported_set.imported_members
            involved_file_members = involved_set.imported_members

            if involved_file_members & imported_file_members:
                # Non-empty intersection between imported and involved members.
                # Return True.
                return True

        # If we've reached the end of iterating through the intersecting files
        # and haven't returned already, then even though there are some files
        # in common, there are no matching members, so we should return False.
        return False

    # Default: Return True to continue normal test collection from this module.
    return True


def build_involved_files_and_members(
    raw_args: List[str]
) -> FrozenSet[Tuple[str, ImportSet]]:
    """Given a list of raw argument values passed into the --involving flag
    from a pytest config object, build a dictionary mapping from the file
    where an object is defined to a set of objects defined in that module
    that the user has requested.

    Args:
        raw_args (List[str]): list of raw arguments provided to the
        --involving flag

    Returns:
        FrozenSet[Tuple[str, FrozenSet[str]]]: Keys are files to check for tests
            involving, values are ImportSets of members in those files.
    """
    involved_files_and_members = {}

    for involved_object in raw_args:
        path = resolve_file_or_module(involved_object)
        member = resolve_member_reference(involved_object)

        if path not in involved_files_and_members:
            involved_files_and_members[path] = ImportSet(path, False)

        if member:
            involved_files_and_members[path].imported_members.add(member)
        else:
            involved_files_and_members[path].has_full_import = True

    return frozenset(involved_files_and_members.items())


def resolve_file_or_module(raw_argument: str) -> str:
    """Given a raw string argument passed to --involving, this function splits
    it by double-colon to get just the bare file or module reference"""
    file_or_module, *_ = raw_argument.split("::")

    if file_or_module.endswith(".py"):
        # .py file specified on command line, so just resolve it
        return str(Path(file_or_module).resolve())
    else:
        # Not a .py file, so probably a module.
        return import_module(file_or_module).__file__


def resolve_member_reference(raw_argument: str) -> Optional[str]:
    """Given a raw string argument passed to --involving, this function splits
    it by double-colon to figure out if it's a reference to a member within
    the provided file or module.

    Args:
        raw_argument (str): the raw argument string to check

    Returns:
        str: the name of the member if present

    Raises:
        ValueError: if there are too many double-colons in the string (max: 1)
    """
    _file_or_module, *path_parts = raw_argument.split("::")

    if len(path_parts) > 1:
        raise ValueError(
            f"{raw_argument} is an invalid member specifier "
            "(there should be maximally one :: in the string)"
        )

    if path_parts:
        return path_parts[0] or None

    return None


def get_members_by_file(module_members: Dict[str, object]) -> Dict[str, ImportSet]:
    """Given a collection of a module's members, return a mapping from the files
    where those members are defined to the names of the members.

    Arguments:
        module_members (Dict[str, object]): Module __dict__ attribute value

    Returns:
        Dict[str, ImportSet]: Mapping from module file name to a set of members
                             imported from the module.
    """
    module_files = {}

    for member_name, member in module_members.items():
        if ismodule(member) and hasattr(member, "__file__"):
            if member.__file__ not in module_files:
                module_files[member.__file__] = ImportSet(member.__file__, True)
            else:
                module_files[member.__file__].has_full_import = True
        else:
            module_name = getattr(member, "__module__", None)
            if module_name:
                module = get_module(module_name)
                if hasattr(module, "__file__"):

                    if module.__file__ not in module_files:
                        module_files[module.__file__] = ImportSet(
                            module.__file__, False
                        )

                    usable_name = getattr(member, "__name__", member_name)

                    if not isinstance(usable_name, Hashable):
                        usable_name = member_name

                    module_files[module.__file__].imported_members.add(usable_name)

    return module_files


def get_module(name):
    """This helper method has been extracted to make it easier to test the
    logic of get_members_by_file"""
    return sys.modules[name]


# endregion
