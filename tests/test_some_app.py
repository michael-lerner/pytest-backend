import time
from datetime import datetime

import pytest
import six


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


def test_delete_values(
    test_client,
    bulk_insert_some_values,
):
    """
    Test that the values are deleted correctly
    """
    for payload in bulk_insert_some_values:
        response = test_client.delete(f'/{payload["id"]}')
        assert response.status_code == 200
        assert response.json() == payload["id"]
        response = test_client.get(f'/{payload["id"]}')
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
