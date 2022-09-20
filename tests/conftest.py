import sys
import os
import pytest
from grants import create_app, db
from helpers.utils import PersonBuilder, HouseholdBuilder

sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))


@pytest.fixture
def client():
    app = create_app(True)
    with app.app_context():
        db.create_all()
        with app.test_client() as test_app:
            test_app.app_context = app.test_request_context()
            test_app.app_context.push()
            yield test_app
        db.drop_all()


@pytest.fixture
def empty_household():
    empty_household = HouseholdBuilder().create()
    return empty_household


@pytest.fixture
def empty_household_saved():
    return HouseholdBuilder().create_and_write()


@pytest.fixture
def person(empty_household):
    person = PersonBuilder(empty_household).create()
    return person


@pytest.fixture
def person_saved(empty_household_saved):
    return PersonBuilder(empty_household_saved).create_and_write()
