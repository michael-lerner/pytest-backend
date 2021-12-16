import sys
import unittest

import fastapi.testclient
import tenacity

from database import fake_db
from main import app


class TestCase(unittest.TestCase):
    """
    Cool things about pytest it can run this code

    """

    test_client = fastapi.testclient.TestClient(app)

    @classmethod
    def setUpClass(cls):
        """
        A SetUpClass function that can be defined once per a test case.
        And run only once.
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

    def setUp(self):
        """
        Some setUp function that can be defined once per a test case and run
        before every test function
        """
        self.test_client.post(
            "/",
            json={"value": "test_case_1", "id": "20"},
        )
        self.test_client.post(
            "/",
            json={"value": "test_case_1", "id": "21"},
        )

    @classmethod
    def teardownClass(cls):
        """
        A SetUpClass function that can be defined once per a test case.
        And run only once after the test is done
        """

    def tearDown(self):
        """
        Some tearDown function that can be defined once per a test case and run
        after every test function
        """
        self.test_client.delete(
            "/20",
        )
        self.test_client.delete(
            "/21",
        )

    def test_case_1(self):
        response = self.test_client.get("/20")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "test_case_1")

    def test_case_2(self):
        response = self.test_client.get("/21")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "test_case_1")

    def test_case_not_found(self):
        response = self.test_client.get("/22")
        self.assertEqual(response.status_code, 404)
