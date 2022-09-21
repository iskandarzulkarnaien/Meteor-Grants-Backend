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


# TODO: Rename these Household Fixtures. Follows naming convention: '<household_type>_<family members...>_<total annual income>_family'
@pytest.fixture
def family1():
    # HDB
    # 2x Adults (married)
    # 2x Teenager Student
    # - Total Annual Income: $60,000
    household = HouseholdBuilder().hdb().create_and_write()

    # Note: Intentionally suppress unused variable warning as these variable assignments make the code more readable
    husband = PersonBuilder(household).gender_male().married().employed(30000).adult().create_and_write()   # noqa: F841
    wife = PersonBuilder(household).gender_female().married().employed(30000).adult().create_and_write()    # noqa: F841
    teen_student1 = PersonBuilder(household).student().teenager().create_and_write()                        # noqa: F841
    teen_student2 = PersonBuilder(household).student().teenager().create_and_write()                        # noqa: F841
    return household


@pytest.fixture
def family2():
    # Landed
    # 2x Adults (married)
    # 1x Teenager Student
    # 1x Adult Student
    # - Total Annual Income: $180,000
    household = HouseholdBuilder().landed().create_and_write()

    husband = PersonBuilder(household).gender_male().married().employed(80000).adult().create_and_write()   # noqa: F841
    wife = PersonBuilder(household).gender_female().married().employed(100000).adult().create_and_write()   # noqa: F841
    teen_student1 = PersonBuilder(household).student().teenager().create_and_write()                        # noqa: F841
    adult_student = PersonBuilder(household).student().adult().create_and_write()                           # noqa: F841
    return household


@pytest.fixture
def family3():
    # Condo
    # 1x Employed Elder
    # 2x Adults (married)
    # 1x Unemployed Teenager
    # - Total Annual Income: $90,000
    household = HouseholdBuilder().condo().create_and_write()

    elder_employed = PersonBuilder(household).gender_male().employed(20000).elder().create_and_write()      # noqa: F841
    husband = PersonBuilder(household).gender_male().married().employed(40000).adult().create_and_write()   # noqa: F841
    wife = PersonBuilder(household).gender_female().married().employed(30000).adult().create_and_write()    # noqa: F841
    teen_unemployed = PersonBuilder(household).unemployed().teenager().create_and_write()                   # noqa: F841
    return household


@pytest.fixture
def all_families(family1, family2, family3):
    return locals().values()
