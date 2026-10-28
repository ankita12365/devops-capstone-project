"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""
import os
import logging
import unittest
from unittest.mock import patch, MagicMock
from service import app
from service.models import Account, DataValidationError, db

DATABASE_URI = os.getenv(
    "DATABASE_URI", "sqlite:///:memory:"
)

BASE_URL = "/accounts"
CONTENT_TYPE_JSON = "application/json"

######################################################################
#  T E S T   C A S E S
######################################################################


class TestAccountService(unittest.TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Account.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once after test suite"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Account).delete()
        db.session.commit()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################
    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for i in range(count):
            account = Account(
                name=f"Test Account {i}",
                email=f"test{i}@example.com",
                address=f"123 Test St #{i}",
                phone_number=f"555-000{i}",
            )
            account.create()
            accounts.append(account)
        return accounts

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the Home Page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = {
            "name": "John Doe",
            "email": "john@example.com",
            "address": "123 Main St",
            "phone_number": "555-1234",
        }
        resp = self.client.post(
            BASE_URL,
            json=account,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertEqual(data["name"], account["name"])
        self.assertEqual(data["email"], account["email"])

    def test_get_account(self):
        """It should Read a single Account"""
        account = self._create_accounts(1)[0]
        resp = self.client.get(f"{BASE_URL}/{account.id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["name"], account.name)

    def test_get_account_not_found(self):
        """It should not Read an Account that is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, 404)

    def test_list_accounts(self):
        """It should List all Accounts"""
        self._create_accounts(3)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(len(data), 3)

    def test_update_account(self):
        """It should Update an existing Account"""
        account = self._create_accounts(1)[0]
        new_account = account.serialize()
        new_account["name"] = "Updated Name"
        resp = self.client.put(
            f"{BASE_URL}/{account.id}",
            json=new_account,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, 200)
        updated = resp.get_json()
        self.assertEqual(updated["name"], "Updated Name")

    def test_delete_account(self):
        """It should Delete an Account"""
        account = self._create_accounts(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{account.id}")
        self.assertEqual(resp.status_code, 204)

    def test_security_headers(self):
        """It should return security headers"""
        resp = self.client.get("/", environ_base={"wsgi.url_scheme": "https"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("X-Content-Type-Options", resp.headers)
        self.assertIn("X-Frame-Options", resp.headers)

    def test_cors_security(self):
        """It should return a CORS header"""
        resp = self.client.get("/", environ_base={"wsgi.url_scheme": "https"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Access-Control-Allow-Origin", resp.headers)


if __name__ == "__main__":
    unittest.main()
