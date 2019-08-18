# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

def get_full_path_for_file(relative_path):
    return Path(relative_path).absolute()

def pytest_addoption(parser):
    """Add the --covering-file command line argument to the pytest argument
    parser via the pytest_addoption hook. We use action=append so that this
    flag can be passed multiple times to build up a list of files to cover"""
    group = parser.getgroup('invert')
    group.addoption(
        '--covering-file',
        action='append',
        help='Python source file(s) to find tests covering'
    )

def pytest_report_header(config):
    """Add the files being covered to the pytest preamble, via the
    pytest_report_header hook"""
    files_covered = config.getoption("--covering-file") or []

    full_file_paths = [
        get_full_path_for_file(f) for f in files_covered
    ]

    if full_file_paths:
        return [
            "Running tests covering files:",
            *[f"    {f}" for f in full_file_paths]
        ]

    return []

def pytest_pycollect_makemodule(path, parent):
    """Skip any module that doesn't have any imports of files you specified
    with the --covering-file argument"""
    # import pdb; pdb.set_trace()
    return False
    pass

def pytest_collectstart(collector):

def pytest_pycollect_makeitem(collector, name, obj):
    # import pdb; pdb.set_trace()
    pass

def pytest_collection_modifyitems(session, config, items):
    # import pdb; pdb.set_trace()
    return items