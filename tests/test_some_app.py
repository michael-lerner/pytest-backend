from datetime import datetime

import pytest


def test_basic_pytest_syntax():
    """
    https://docs.pytest.org/en/6.2.x/
    Read this to understand pytest syntax better
    """

    # pytest uses assert statements to check if the test passes
    assert "test" == "test"
    # It can check also more complicated data types
    assert {"1": "1"} == {"1": "1"}

    # It will also have some insights on why your test failed
    # assert ['1', '2'] == ['1', '2', '3'] # Uncomment for failing test
    """
    ['1', '2'] != ['1', '2', '3']

    Expected :['1', '2', '3']
    Actual   :['1', '2']
    """
    # You can also give some costume messages if failed with basic assert syntax
    # assert statement , "This is a custom message"
    # this can be used also to document the test a bit for your future self or return let's say the error from the
    # response in an API call
    # Uncomment for failing test  # Uncomment for failing test
    # assert {'1', "1"} == {'1', "2"}, 'Sets are not equal fatal bug!!!!!!!!'
    """    
    AssertionError: Sets are not equal fatal bug!!!!!!!!
    assert {'1'} == {'1', '2'}
      Extra items in the right set:
      '2'
      Full diff:
      - {'1', '2'}
      + {'1'}
    """
    # Lets say you really miss self.assertAlmostEqual from unittest great you have it here also
    # This will help you check the dreaded floats
    assert 2.2 == pytest.approx(2.3, 0.1), "OMG floats are not almost equal"


@pytest.mark.parametrize(
    argnames=["add_value"],
    indirect=["add_value"],
    argvalues=[
        ({"id": "1", "value": "test1"},),
        ({"id": "2", "value": "test1"},),
    ],
)
def test_get_value(
    test_client,
    add_value,
):
    """
    Test that the value is returned correctly
    Cool pytest things here:
    1) We can give it different parameters for each test
    2) We can use the add_value fixture to add a value
    3) add_value also cleans up the value after the test
    4) The fixture can also return a value
    5) As this fixture is indirect we can give it values from parameters
    """
    response = test_client.get(f'/{add_value["id"]}')
    assert response.status_code == 200
    assert response.json() == add_value["value"]


def test_get_values(test_client, bulk_insert_some_values):
    """
    Test that the values are returned correctly
    Cool pytest things here:
    1) New Test new setup unlike the unit test module that supports
        def setUp(self):
        and
        @classmethod
        def setUpClass(cls):
        ...
        This helps us not worry about side effects in tests
    """
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"values": bulk_insert_some_values}


@pytest.mark.parametrize(
    argnames="id_",
    argvalues=[
        "1",
        "2",
        "3",
        pytest.param("notAnId", marks=pytest.mark.xfail),
    ],
)
def test_delete_values(
    test_client,
    bulk_insert_some_values,
    id_,
):
    """
    Test that the values are deleted correctly
    Cool pytest things here:
    we can mark a param as expected to fail pytest.param("notAnId", marks=pytest.mark.xfail)
    we can have costume parameters from @pytest.mark.parametrize
    And then we will have output per a parameter no more
    for test_case in test_cases:
        self.assertTrue(statement)
    we can also just know what test case failed
    """
    response = test_client.delete(f"/{id_}")
    assert response.status_code == 200
    assert response.json() == id_
    response = test_client.get(f"/{id_}")
    assert response.status_code == 404


@pytest.mark.timeout(1)
@pytest.mark.parametrize(
    argnames="num_secs",
    argvalues=[
        1,
        2,
    ],
)
def test_long_running_task(mock_sleep, test_client, num_secs):
    """
    Test that the long running task is run correctly
    Cool pytest things here:
    1) Can be added per a test and even per a Session and reset with yield
    2) pytest mark has loads of features like timeout , skip, xfail, async etc
    3) With pytest.mark.timeout you can validate easily that something mission critical is not taking too long
    """
    response = test_client.get("/long_running_task/", params={"num_secs": num_secs})
    assert response.status_code == 200
    mock_sleep.assert_called_once_with(
        num_secs,
    )  # you can see that the fixture reset the mock after each test


def test_long_running_task_no_mock(test_client):
    """
    Cool pytest things here:
    1) The mock is not used here and it is easy to mock or not mock something depending on the needs
    """
    response = test_client.get("/long_running_task/", params={"num_secs": 1})
    assert response.status_code == 200


def test_show_auto_use(test_client):
    """
    Cool pytest things here:
    1) As you can see freeze the time mock is auto used here and time is frozen
    datetime.now() == the response
    """
    response = test_client.get("/get_datetime_now/")
    assert response.status_code == 200
    assert response.json() == datetime.now().isoformat()


def test_show_auto_use_2(test_client, freeze_the_time):
    """
    We can also use the freeze_the_time fixture to get the value the fixture returns
    """
    response = test_client.get("/get_datetime_now/")
    assert response.status_code == 200
    assert response.json() == freeze_the_time.isoformat()


@pytest.mark.asyncio
async def test_async_route(test_client):
    """
    Cool pytest things here:
    !) So by using the pytest.mark.asyncio we can mark the test as async
    and can call an async route we delagate the Async loop orechastration to pytest-asyncio
    """
    response = test_client.get("/async_route/")
    assert response.status_code == 200
    assert response.json() == 200


@pytest.mark.xfail
@pytest.mark.asyncio
async def test_this_route_has_some_thing_i_dont_want(test_client):
    """
    An Article: https://blog.ganssle.io/articles/2021/11/pytest-xfail.html
    Cool pytest things here:
    Let's say we found a bug in this route
    In pytest you can run pytest.mark.xfail to mark the test as expected to fail
    If the bug is fixed we can just remove the pytest.mark.xfail from the tests
    This is a lot more friendly way to than ways to reproduce the bug that we have in the JIRA
    """
    response = test_client.get("/this_route_has_some_thing_i_dont_want/")
    assert response.status_code == 200
    assert response.json() == 2  # I wanted this API call to return 2 it returns 1


def test_long_setup_test(
    test_client,
    some_fixture_that_needs_other_fixture,
):
    """
    This is a long setup test
    test_client: you can see that we can pass the test_client fixture to the test, although
    it is used in some_fixture_that_needs_other_fixture.
    All the cleanups are done after yield both for bulk_insert_some_values and some_fixture_that_needs_other_fixture
    Pytest knows how to handle this.
    So we can combine fixtures with other fixtures and also get the fixtures directly into our test
    """
    response = test_client.get(f"/{some_fixture_that_needs_other_fixture}")
    assert response.status_code == 200
    assert response.json() == "extra_value"
