"""
Models for Account Service

All of the models are stored in this module

Models
------
Account - An account in the system

Attributes
----------
id          (integer) - the unique id of the account
name        (string)  - the name of the account owner
email       (string)  - the email address of the account
address     (string)  - the address of the account owner
phone_number (string) - the phone number of the account owner
date_joined (date)    - the date the account was created
"""
import logging
from datetime import date
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Account.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


######################################################################
# P E R S I S T E N T   B A S E   M O D E L
######################################################################
class PersistentBase:
    """Base class added persistent methods"""

    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    def create(self):
        """
        Creates an Account to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates an Account to the database
        """
        logger.info("Updating %s", self.name)
        db.session.commit()

    def delete(self):
        """Removes an Account from the data store"""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)


######################################################################
# A C C O U N T   M O D E L
######################################################################
class Account(db.Model, PersistentBase):
    """
    Class that represents an Account
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    address = db.Column(db.String(256))
    phone_number = db.Column(db.String(32), nullable=True)
    date_joined = db.Column(db.Date(), nullable=False, default=date.today())

    def __repr__(self):
        return f"<Account {self.name} id=[{self.id}]>"

    def serialize(self):
        """Serializes an Account into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "phone_number": self.phone_number,
            "date_joined": str(self.date_joined),
        }

    def deserialize(self, data):
        """
        Deserializes an Account from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.email = data["email"]
            self.address = data["address"]
            self.phone_number = data.get("phone_number")
            if "date_joined" in data:
                self.date_joined = date.fromisoformat(data["date_joined"])
        except KeyError as error:
            raise DataValidationError(
                "Invalid Account: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Account: body of request contained bad or no data - "
                "Error message: " + str(error)
            ) from error
        return self
