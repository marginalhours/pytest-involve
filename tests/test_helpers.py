# -*- coding: utf-8 -*-
"""This module contains unit tests for the helpers in pytest_involve.py"""
from unittest import mock
from pathlib import Path

import pytest

from pytest_involve import (
    build_involved_files_and_members,
    get_involved_files_and_members,
    get_involved_objects,
    get_members_by_file,
    resolve_member_reference,
    should_module_be_included,
)


MODULE = "pytest_involve"


@mock.patch(MODULE + ".resolve_member_reference", autospec=True)
@mock.patch(MODULE + ".resolve_file_or_module", autospec=True)
def test_build_involved_files_and_members(mock_resolve_file, mock_resolve_member):
    """Test that build_involved_files_and_members returns a filter dictionary
    of module files and members within them"""
    mock_input = [
        "./module/file_one.py",
        "./module/file_two.py::function_two",
        "./module/file_three.py::function_three",
        "./module/file_three.py::ClassThree",
    ]

    mock_resolve_file.side_effect = [
        "file_one.py",
        "file_two.py",
        "file_three.py",
        "file_three.py",
    ]

    mock_resolve_member.side_effect = [
        None,
        "function_two",
        "function_three",
        "ClassThree",
    ]

    result = build_involved_files_and_members(mock_input)

    assert result == frozenset(
        [("file_one.py", frozenset()),
        ("file_two.py", frozenset({"function_two"})),
        ("file_three.py", frozenset({"function_three", "ClassThree"}))],
    )

    assert mock_resolve_file.mock_calls == [mock.call(f) for f in mock_input]
    assert mock_resolve_member.mock_calls == [mock.call(f) for f in mock_input]


@mock.patch(MODULE + ".build_involved_files_and_members", autospec=True)
@mock.patch(MODULE + ".get_involved_objects", autospec=True)
def test_get_involved_files_and_members(mock_get_involved, mock_build_involved):
    """Test that get_involved_files_and_members calls
    build_involved_files_and_members with the value of the --involved arguments
    """
    mock_config = mock.Mock()

    get_involved_files_and_members(mock_config)

    mock_get_involved.assert_called_with(mock_config)
    mock_build_involved.assert_called_with(mock_get_involved.return_value)


def test_get_involved_objects():
    """Test that get_involved_objects looks up the objects in the config"""
    mock_config = mock.Mock()
    mock_config.getoption.return_value = ["one.py", "two.py::Class"]

    assert get_involved_objects(mock_config) == ["one.py", "two.py::Class"]


@mock.patch(MODULE + ".ismodule", autospec=True)
def test_get_members_by_file(mock_is_module):
    """Test that get_members_by_file returns the
    correct list of (object, filename) tuples"""
    mock_is_module.return_value = True

    mock_member_1 = mock.Mock()
    mock_member_1.__name__ = "mock_module_1"
    mock_member_1.__file__ = "one.py"

    mock_member_2 = mock.Mock()
    mock_member_2.__name__ = "mock_module_2"
    mock_member_2.__file__ = "two.py"

    assert get_members_by_file({
        "mock_module_1": mock_member_1,
        "mock_module_2": mock_member_2
    }) == {
        "one.py": {"mock_module_1"},
        "two.py": {"mock_module_2"}
    }


@mock.patch(MODULE + ".get_members_by_file", autospec=True)
def test_should_module_be_included(mock_get_members):
    """Tests that should_module_be_included filters out modules not importing
    relevant objects"""
    mock_get_members.return_value = {"one.py": {"member_one"}, "two.py": {"member_two"}}

    assert should_module_be_included(mock.Mock(), frozenset([
        ("one.py", frozenset(["member_one"])),
        ("two.py", frozenset(["member_two"]))
    ])) == True


@pytest.mark.parametrize(
    "input, expected",
    [
        ("~/module/file.py", None),
        ("~/module/file.py::func_name", "func_name"),
        ("~/module/file.py::ClassName", "ClassName"),
        ("module.file", None),
        ("module.file::func_name", "func_name"),
        ("module.file::ClassName", "ClassName"),
    ],
)
def test_resolve_member_reference(input, expected):
    """Test that resolve_member_reference handles files and modules with members
    specified and without"""
    assert resolve_member_reference(input) == expected


def test_resolve_member_reference_raises():
    """Test that resolve_member_reference raises a ValueError when the member
    specifier has multiple double-colons in"""
    with pytest.raises(ValueError):
        resolve_member_reference("~/module/file.py::one::two")

    with pytest.raises(ValueError):
        resolve_member_reference("module.file::one::two")
