# -*- coding: utf-8 -*-
"""This module contains tests for the pytest_involve pytest plugin."""

def make_multiple_modules(test_dir_fixture, file_names):
    """Given a test directory fixture, create test files
    corresponding to the list of names passed in. Every file
    will contain one function and one class with names based
    on the file_names.

    Arguments:
        test_dir_fixture {fixture} -- pytest test_dir fixture
        file_names {List[str]} -- List of module names
    """
    test_dir_fixture.makepyfile(
        **{
            name: f"""
                def func_{name}():
                    return "{name}"

                class Class{name.title()}:
                    pass
            """
            for name in file_names
        }
    )

def test_collection_of_single_file(testdir):
    """Test that a single python file can be passed via the
    --involving optional argument"""
    make_multiple_modules(testdir, ["one"])

    testdir.makepyfile(test_one="""
        import one

        def test_func_one():
            assert one.func_one() == "one"
    """)

    result = testdir.runpytest(
        "--involving=./one.py",
        "-v"
    )

    result.stdout.fnmatch_lines([
         "Running tests involving:",
         "*/one.py",
         "test_one.py::test_func_one PASSED*"
    ])

    assert result.ret == 0

def test_collection_of_multiple_files(testdir):
    """Test that test cases for multiple files can be collected using the
    --involving argument multiple times"""
    make_multiple_modules(testdir, ["one", "two"])

    testdir.makepyfile(
        test_one="""
            import one

            def test_func_one():
                assert one.func_one() == "one"
        """,
        test_two="""
            import two

            def test_func_two():
                assert two.func_two() == "two"
        """
    )

    result = testdir.runpytest(
        "--involving=./one.py",
        "--involving=./two.py",
        "-v"
    )

    result.stdout.fnmatch_lines([
        "Running tests involving:",
        "*/one.py",
        "*/two.py",
        "test_one.py::test_func_one PASSED*",
        "test_two.py::test_func_two PASSED*"
    ])

    assert result.ret == 0


def test_collection_from_single_file_multiple_files_present(testdir):
    """Test collecting a single file importing a relevant module when
    multiple files are present"""
    make_multiple_modules(testdir, ["one", "two"])

    testdir.makepyfile(
        test_one="""
            import one

            def test_func_one():
                assert one.func_one() == "one"
        """,
        test_two="""
            import two

            def test_func_two():
                assert two.func_two() == "two"
        """
    )

    result = testdir.runpytest(
        "--involving=./one.py",
        "-v"
    )

    result.stdout.fnmatch_lines([
         "Running tests involving:",
         "*/one.py",
         "test_one.py::test_func_one PASSED*"
    ])

    assert result.ret == 0


def test_collection_from_file_member_collects(testdir):
    """Test collecting a single file importing a member from a relevant
    module"""
    make_multiple_modules(testdir, ["one"])

    testdir.makepyfile(test_one="""
        from one import func_one

        def test_func_one():
            assert func_one() == "one"
    """)

    result = testdir.runpytest(
        "--involving=./one.py",
        "-v"
    )

    result.stdout.fnmatch_lines([
         "Running tests involving:",
         "*/one.py",
         "test_one.py::test_func_one PASSED*"
    ])

    assert result.ret == 0


def test_collection_from_file_member_collects_other_doesnt(testdir):
    """Test collecting a single module member from a file in a case where
    a different member is imported into another file"""
    testdir.makepyfile(
        one="""
            def func_one():
                return "one"

            def func_two():
                return "two"
        """
    )

    testdir.makepyfile(test_one="""
        from one import func_one

        def test_func_one():
            assert func_one() == "one"
    """, test_two="""
        from one import func_two

        def test_func_two():
            assert func_two() == "two"
    """)

    result = testdir.runpytest(
        "--involving=./one.py::func_one",
        "-v"
    )

    result.stdout.fnmatch_lines([
         "Running tests involving:",
         "*/one.py::func_one",
         "test_one.py::test_func_one PASSED*"
    ])

    assert result.ret == 0

def test_collection_from_module_whole_module(testdir):
    """Test specifying a single module name rather than a file"""
    assert False

def test_collection_from_module_member_collects(testdir):
    """Test specifying a module member rather than a whole module"""
    assert False


def test_collection_from_module_member_collects_other_doesnt(testdir):
    """Test collecting a single module member in a case where a different member
    is imported into another file"""
    assert False


def test_proceeds_as_normal_if_arg_not_provided(testdir):
    """Test that if --involving is not provided then test collection
    happens as normal"""
    assert False


