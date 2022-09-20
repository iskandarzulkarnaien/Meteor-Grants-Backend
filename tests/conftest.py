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


# TODO: Find better names for the below fixtures
@pytest.fixture
def family1(empty_household_saved):
    # 2x Adults (married)
    # 2x Teenager Student
    # - Total Annual Income: $60,000
    household = empty_household_saved

    # Note: Intentionally suppress unused variable warning as these variable assignments make the code more readable
    husband = PersonBuilder(household).gender_male().married().employed(30000).adult().create_and_write()   # noqa: F841
    wife = PersonBuilder(household).gender_female().married().employed(30000).adult().create_and_write()    # noqa: F841
    student1 = PersonBuilder(household).student().teenager().create_and_write()                             # noqa: F841
    student2 = PersonBuilder(household).student().teenager().create_and_write()                             # noqa: F841
    return household
