# -*- coding: utf-8 -*-
"""This module contains unit tests for the helpers in pytest_involve.py"""
import pytest
from unittest import mock
from pytest_involve import (
    build_involved_files_and_members,
    get_file_attribute_for_module,
    get_full_path_for_file,
    get_involved_files_and_members,
    get_involved_objects,
    get_original_files_members_were_defined_in,
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

def test_get_file_attribute_for_module():
    """Test that get_file_attribute imports the module and returns the
    __file__ attribute"""
    import_mock = mock.Mock()
    import_mock.return_value.__file__ = mock.Mock()

    with mock.patch("builtins.__import__", side_effect=import_mock):
        module_file = get_file_attribute_for_module("some.module")

    assert module_file == import_mock.return_value.__file__


def test_get_full_path_for_file():
    assert False


def test_get_involved_files_and_members():
    assert False


def test_get_involved_objects():
    assert False


def test_get_original_files_members_were_defined_in():
    assert False


def test_should_module_be_included():
    assert False


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
