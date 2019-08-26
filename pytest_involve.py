# -*- coding: utf-8 -*-
import sys
from functools import lru_cache
from inspect import ismodule
from pathlib import Path

import pytest


def get_full_path_for_file(relative_path):
    """Given a path provided on the command line, make it canonical"""
    return str(Path(relative_path).resolve())


@lru_cache()
def get_full_file_paths_from_config(config):
    """Given a pytest config, return the set of files specified by the
    --involving flag"""
    files_covered = config.getoption("--involving") or []

    full_file_paths = frozenset(get_full_path_for_file(f) for f in files_covered)

    return full_file_paths


@lru_cache()
def should_module_be_included(module, requested_files):
    """Work out if a module should be included, exactly once"""
    imported_module_files = get_original_files_members_were_defined_in(
        module.__dict__.values()
    )

    if not requested_files & imported_module_files:
        return []

    return None


def get_original_files_members_were_defined_in(module_members):
    """Given a module, track down the original files that all its members
    were defined in"""
    module_files = set()

    for member in module_members:
        if ismodule(member) and hasattr(member, "__file__"):
            module_files.add(member.__file__)
        else:
            module_name = getattr(member, "__module__", None)
            if module_name:
                module = sys.modules[module_name]
                if hasattr(module, "__file__"):
                    module_files.add(module.__file__)
    return module_files


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
    full_file_paths = get_full_file_paths_from_config(config)

    if full_file_paths:
        return [
            "Running tests involving:",
            *[f"    {f}" for f in sorted(full_file_paths)],
        ]

    return []


def pytest_pycollect_makeitem(collector, name, obj):
    """Don"t collect from modules that don"t import any file we care about"""
    requested_files = get_full_file_paths_from_config(collector.config)

    if requested_files:
        return should_module_be_included(collector.module, requested_files)

    return None
