# -*- coding: utf-8 -*-

def test_collection_of_single_file(testdir):
    """Test that a single python file can be passed via the
    --covering-file optional argument"""
    testdir.makepyfile(one="""
        def func_one():
            return 5
    """)

    testdir.makepyfile(test_one="""
        from one import func_one

        def test_func_one():
            assert func_one() == 5
    """)

    result = testdir.runpytest(
        "--covering-file=./one.py",
        "-v"
    )

    result.stdout.fnmatch_lines([
         "Running tests covering files:",
         "    ./one.py"
    ])

    assert result.ret == 0

def test_collection_of_multiple_files(testdir):
    """Test that a non-python file will raise an error if passed via the
    --covering-file optional argument"""
    testdir.makepyfile(
        one="""
        def func_one():
            return 5
        """,
        two="""
        def func_two():
            return 6
        """
    )

    testdir.makepyfile(
        test_one="""
            from one import func_one

            def test_func_one():
                assert func_one() == 5
        """,
        test_two="""
            from two import func_two

            def test_func_two():
                assert func_two() == 6
        """
    )

    result = testdir.runpytest(
        "--covering-file=./one.py",
        "--covering-file=./two.py",
        "-v"
    )

    result.stdout.fnmatch_lines([
         "Running tests covering files:",
         "    ./one.py",
         "    ./two.py"
    ])

    assert result.ret == 0


def test_collection_of_non_py_files(testdir):
    """Test that multiple python files can be passed via the
    --covering-file optional argument"""
    assert False


def test_proceeds_as_normal_if_arg_not_provided(testdir):
    """Test that if --covering-file is not provided then test collection
    happens as normal"""

# def test_bar_fixture(testdir):
#     """Make sure that pytest accepts our fixture."""

#     # create a temporary pytest test module
#     testdir.makepyfile("""
#         def test_sth(bar):
#             assert bar == "europython2015"
#     """)

#     # run pytest with the following cmd args
#     result = testdir.runpytest(
#         '--foo=europython2015',
#         '-v'
#     )

#     # fnmatch_lines does an assertion internally
#     result.stdout.fnmatch_lines([
#         '*::test_sth PASSED*',
#     ])

#     # make sure that that we get a '0' exit code for the testsuite
#     assert result.ret == 0


# def test_help_message(testdir):
#     result = testdir.runpytest(
#         '--help',
#     )
#     # fnmatch_lines does an assertion internally
#     result.stdout.fnmatch_lines([
#         'invert:',
#         '*--foo=DEST_FOO*Set the value for the fixture "bar".',
#     ])


# def test_hello_ini_setting(testdir):
#     testdir.makeini("""
#         [pytest]
#         HELLO = world
#     """)

#     testdir.makepyfile("""
#         import pytest

#         @pytest.fixture
#         def hello(request):
#             return request.config.getini('HELLO')

#         def test_hello_world(hello):
#             assert hello == 'world'
#     """)

#     result = testdir.runpytest('-v')

#     # fnmatch_lines does an assertion internally
#     result.stdout.fnmatch_lines([
#         '*::test_hello_world PASSED*',
#     ])

#     # make sure that that we get a '0' exit code for the testsuite
#     assert result.ret == 0
