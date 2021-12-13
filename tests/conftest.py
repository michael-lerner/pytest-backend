import time

import pytest

from main import app
from fastapi.testclient import TestClient
import pytest_mock


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    """
    Cool pytest things:
    Client can be created once per a session saving us a lot in load times
    in case of unit tests also mocks can be added here with if the app was using a factory method
    and reset after each test
    """
    yield TestClient(app)


@pytest.fixture
def add_value(test_client, request):
    payload = request.param
    response = test_client.post('/', json={'value': payload['value'], 'id': payload['id']})
    assert response.status_code == 200
    yield payload
    response = test_client.delete(f'/{payload["id"]}')
    assert response.status_code in [200, 404]


@pytest.fixture
def bulk_insert_some_values(test_client) -> list[dict[str, str]]:
    payloads = []
    for value_and_id in range(10):
        payload = {'value': str(value_and_id), 'id': str(value_and_id)}
        response = test_client.post('/', json=payload)
        assert response.status_code == 200
        payloads.append(payload)
    yield payloads
    for value_and_id in payloads:
        response = test_client.delete(f'/{value_and_id["id"]}')
        assert response.status_code in [200, 404]


@pytest.fixture
def mock_sleep(mocker: pytest_mock.MockerFixture):
    """
    Cool pytest things:
    Mocks can be used as a fixture and yield also if you want you can add return value/sideaffect through params like
    in add_value.
    also the mock is reset after yield with resetall if needed

    """
    _mock = mocker.patch('time.sleep', spec=time.sleep)
    yield _mock
    _mock.resetall()
