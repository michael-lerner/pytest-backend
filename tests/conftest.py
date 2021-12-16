import sys
import time
from datetime import datetime

import fastapi
import freezegun
import pytest
import tenacity

from main import app
from database import fake_db
from fastapi.testclient import TestClient
import pytest_mock


@pytest.fixture(scope="session", autouse=True)
def get_db():
    """
    Let's say we want to initialize the db
    and not run some python3 -m path_to_module.database.initialize_db() before the test every time,
    and we want it also to run in CI. easier so let's do it here once per test.
    See that we use it once per session, not once per test.
    And we autouse it
    """
    for attempt in tenacity.Retrying(
        wait=tenacity.wait.wait_fixed(
            wait=0.001,
        ),
        retry=tenacity.retry_if_exception_type(
            exception_types=RuntimeError,
        ),
        stop=tenacity.stop_after_attempt(
            max_attempt_number=7,
        ),
        before_sleep=print("waiting for DB", file=sys.stderr),
        reraise=True,
    ):
        with attempt:
            fake_db.fake_initialize_db()
            yield fake_db


@pytest.fixture(scope="session")
def app_() -> fastapi.FastAPI:
    """
    Cool pytest things:
    We can create a fixture that will be used by all the tests
    """
    return app


@pytest.fixture(scope="session")
def test_client(app_) -> TestClient:
    """
    Cool pytest things:
    Client can be created once per a session saving us a lot in load times
    in case of unit tests also mocks can be added here with if the app was using a factory method
    and reset after each test
    """
    yield TestClient(app_)


@pytest.fixture
def add_value(test_client, request) -> dict[str, str]:
    payload = request.param
    response = test_client.post(
        "/",
        json={"value": payload["value"], "id": payload["id"]},
    )
    assert response.status_code == 200
    yield payload
    response = test_client.delete(f'/{payload["id"]}')
    assert response.status_code in [200, 404]


@pytest.fixture(
    params=[
        {"id": "1", "value": "test1"},
        {"id": "2", "value": "test1"},
    ],
)
def add_value_fixture_params(test_client, request) -> dict[str, str]:
    payload = request.param
    response = test_client.post(
        "/",
        json={"value": payload["value"], "id": payload["id"]},
    )
    assert response.status_code == 200
    yield payload
    response = test_client.delete(f'/{payload["id"]}')
    assert response.status_code in [200, 404]


@pytest.fixture
def delete_value(test_client, request) -> None:
    payload = request.param
    yield
    response = test_client.delete(f"/{payload}")
    assert response.status_code in [200, 404]


@pytest.fixture
def bulk_insert_some_values(test_client) -> list[dict[str, str]]:
    payloads = []
    for value_and_id in range(10):
        payload = {"value": str(value_and_id), "id": str(value_and_id)}
        response = test_client.post("/", json=payload)
        assert response.status_code == 200
        payloads.append(payload)
    yield payloads
    for value_and_id in payloads:
        response = test_client.delete(f'/{value_and_id["id"]}')
        assert response.status_code in [200, 404]


@pytest.fixture
def mock_sleep(mocker: pytest_mock.MockerFixture):
    """
    # https://pypi.org/project/pytest-mock/
    Cool pytest things:
    Mocks can be used as a fixture and yield also if you want you can add return value/sideaffect through params like
    in add_value.
    also the mock is reset after yield with resetall if needed

    """
    _mock = mocker.patch("time.sleep", spec=time.sleep)
    yield _mock
    mocker.resetall()


@pytest.fixture
# @pytest.fixture(autouse=True)
def freeze_the_time() -> datetime:
    """
    This is a session fixture that is autouse=True.
    This means that it will be executed for every test in the session.
    Let's say we want to freeze time
    """
    with freezegun.freeze_time(datetime(2020, 1, 1, 0, 0, 0)) as frozen_time:
        yield frozen_time()


@pytest.fixture
def some_fixture_that_needs_other_fixture(
    get_db,
    test_client,
    bulk_insert_some_values,
) -> str:
    """
    Let's say we have a test that needs some other fixture.
    For example , we want to use the db and the test client.
    We can use the fixtures in the same order as we want.

    Some real life example can be updated some value in the db
    and then update another that needs that value to exist
    """
    get_db.add_value(
        id_="extra_id",
        value="extra_value",
    )
    yield "extra_id"
    get_db.remove_value(
        id_="extra_id",
    )
