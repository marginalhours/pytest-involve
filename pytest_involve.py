# -*- coding: utf-8 -*-
import sys
from functools import lru_cache
from inspect import ismodule
from pathlib import Path
from typing import Dict, List, Set, Optional, FrozenSet, Tuple
from types import ModuleType

import pytest

# region pytest hooks


def pytest_addoption(parser):
    """Add the --involving command line argument to the pytest argument
    parser via the pytest_addoption hook. We use action=append so that this
    flag can be passed multiple times to build up a list of files to cover"""
    group = parser.getgroup("involve")
    group.addoption(
        "--involving",
        action="append",
        help="Python source files, modules, or module members to find tests involving",
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
    """Don"t collect from modules that don"t import any file we care about"""
    involved_files_and_members = get_involved_files_and_members(collector.config)

    if involved_files_and_members:
        return should_module_be_included(collector.module, involved_files_and_members)

    return None


# endregion


def resolve_member_reference(raw_argument: str) -> Optional[str]:
    """Given a raw string argument passed to --involving, this function splits
    it by double-colon to figure out if it's a reference to a member within
    the provided file or module.

    Args:
        raw_argument: str -- the raw argument string to check

    Returns:
        str -- the name of the member if present

    Raises:
        ValueError -- if there are too many double-colons in the string (max: 1)
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


def resolve_file_or_module(raw_argument: str) -> str:
    """Given a raw string argument passed to --involving, this function splits
    it by double-colon to get just the bare file or module reference"""
    file_or_module, *_ = raw_argument.split("::")

    if file_or_module.endswith(".py"):
        # Easy case -- file specified on command line, so just resolve it
        return get_full_path_for_file(file_or_module)
    else:
        # Slightly trickier, a module name. Import it then return its __file__
        # attribute
        return get_file_attribute_for_module(file_or_module)


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
        config -- pytest config object

    Returns:
        Dict[str, Set[str]] -- Output of build_involved_files_and_members
    """
    return build_involved_files_and_members(get_involved_objects(config))


@lru_cache()
def should_module_be_included(module: ModuleType, involved_filter: Dict[str, Set[str]]):
    """Given a Python module and a dictionary filter object of files and members
    specified with the --involving flag, decide if tests from the module
    should be included in the pytest run.

    Arguments:
        module {ModuleType} -- The module about which a decision should be made
        involved_filter {Dict[str, Set[str]]} -- The filter of involved files
                                                 and members to check if the
                                                 module imports
    Returns:
        [] or None -- [] to avoid collecting test from the module, None to
                      return control to pytest
    """
    imported_module_files = get_original_files_members_were_defined_in(
        module.__dict__
    )

    if not involved_filter & imported_module_files:
        return []

    return None


def get_full_path_for_file(relative_path) -> str:
    """Given a path provided on the command line, make it canonical"""
    return str(Path(relative_path).resolve())


def get_file_attribute_for_module(module_name) -> str:
    """Given the name of a module, import that module and return the value
    of its __file__ attribute.

    Args:
        module_name {str} -- Name of the module to import

    Returns:
        str -- The location the module was imported from.
    """
    return __import__(module_name).__file__


def build_involved_files_and_members(raw_args: List[str]) -> Dict[str, Set[str]]:
    """Given a list of raw argument values passed into the --involving flag
    from a pytest config object, build a dictionary mapping from the file
    where an object is defined to a set of objects defined in that module
    that the user has requested.

    Args:
        raw_args {List[str]} -- list of raw arguments

    Returns:
        FrozenSet[str, FrozenSet[str]] -- Keys are files to check for tests
                                          involving, values are Sets of members
                                          in those files
    """
    involved_files_and_members = {}

    for involved_object in raw_args:
        path = resolve_file_or_module(involved_object)
        member = resolve_member_reference(involved_object)

        if not path in involved_files_and_members:
            involved_files_and_members[path] = set()

        if member:
            involved_files_and_members[path].add(member)

    return frozenset((k, frozenset(v)) for k, v in involved_files_and_members.items())


def get_original_files_members_were_defined_in(module_members: Dict[str, object]) -> List[Tuple[str, str]]:
    """Given a collection of a module's members, return a list of tuples
    of what those members are called and which file they were originally defined
    in.

    Arguments:
        module_members {Dict[str, object]} -- Module __dict__ attribute value

    Returns:
        List[Tuple[str, str]] -- List of (name of member, name of file it's defined in)
                                 tuples
    """
    module_files = set()

    for member_name, member in module_members.items():
        if ismodule(member) and hasattr(member, "__file__"):
            module_files.add(member.__name__, member.__file__)
        else:
            module_name = getattr(member, "__module__", None)
            if module_name:
                module = sys.modules[module_name]
                if hasattr(module, "__file__"):
                    if hasattr(member, "__name__"):
                        module_files.add(member.__name__, module.__file__)
                    else:
                        module_files.add(member_name, module.__file__)
    return module_files
