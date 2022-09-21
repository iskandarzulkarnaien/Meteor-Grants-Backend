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
    # Total 4x
    # 2x Adults (married)
    # 2x Teenager Student
    # - Total Annual Income: $60,000
    household = HouseholdBuilder().hdb().create_and_write()

    # Note: Intentionally suppress unused variable warning as these variable assignments make the code more readable
    # Note: Names intentionally appended with '-123' to make them unique (i.e. unable to be generated by faker) for testing purposes
    husband = PersonBuilder(household).name('Bob-123').gender_male().married().employed(30000).adult().create_and_write()           # noqa: F841
    wife = PersonBuilder(household).name('Alice-123').gender_female().married(husband).employed(30000).adult().create_and_write()   # noqa: F841
    teen_student1 = PersonBuilder(household).student().teenager().create_and_write()                                            # noqa: F841
    teen_student2 = PersonBuilder(household).student().teenager().create_and_write()                                            # noqa: F841
    return household


@pytest.fixture
def family2():
    # Landed
    # Total: 4x
    # 2x Adults (married)
    # 1x Teenager Student
    # 1x Adult Student
    # - Total Annual Income: $180,000
    household = HouseholdBuilder().landed().create_and_write()

    husband = PersonBuilder(household).gender_male().married().employed(80000).adult().create_and_write()           # noqa: F841
    wife = PersonBuilder(household).gender_female().married(husband).employed(100000).adult().create_and_write()    # noqa: F841
    teen_student1 = PersonBuilder(household).name('Cody-123').student().teenager().create_and_write()                   # noqa: F841
    adult_student = PersonBuilder(household).student().adult().create_and_write()                                   # noqa: F841
    return household


@pytest.fixture
def family3():
    # Condo
    # Total: 6x
    # 1x Employed Elder
    # 2x Adults (married)
    # 3x Unemployed Teenager
    # - Total Annual Income: $90,000
    household = HouseholdBuilder().condo().create_and_write()

    elder_employed = PersonBuilder(household).gender_male().employed(20000).elder().create_and_write()              # noqa: F841
    husband = PersonBuilder(household).gender_male().married().employed(40000).adult().create_and_write()           # noqa: F841
    wife = PersonBuilder(household).gender_female().married(husband).employed(30000).adult().create_and_write()     # noqa: F841
    teen_unemployed1 = PersonBuilder(household).unemployed().teenager().create_and_write()                          # noqa: F841
    teen_unemployed2 = PersonBuilder(household).unemployed().teenager().create_and_write()                          # noqa: F841
    teen_unemployed3 = PersonBuilder(household).unemployed().teenager().create_and_write()                          # noqa: F841

    return household


@pytest.fixture
def family4():
    # HDB
    # Total: 5x
    # 2x Unemployed Elder
    # 1x Adult (widowed)
    # 2x Teenager
    # - Total Annual Income: $30,000
    household = HouseholdBuilder().hdb().create_and_write()

    elder_unemployed1 = PersonBuilder(household).gender_male().unemployed().elder().create_and_write()      # noqa: F841
    elder_unemployed2 = PersonBuilder(household).gender_female().unemployed().elder().create_and_write()    # noqa: F841
    wife = PersonBuilder(household).gender_female().widowed().employed(30000).adult().create_and_write()    # noqa: F841
    teen_unemployed1 = PersonBuilder(household).unemployed().teenager().create_and_write()                  # noqa: F841
    teen_unemployed2 = PersonBuilder(household).unemployed().teenager().create_and_write()                  # noqa: F841

    return household


@pytest.fixture
def family5():
    # Landed
    # Total: 4x
    # 1x Unemployed Elder
    # 2x Unemployed Adult
    # 1x Employed Adult
    # - Total Annual Income: $25000
    household = HouseholdBuilder().landed().create_and_write()

    elder_unemployed = PersonBuilder(household).unemployed().elder().create_and_write()                                 # noqa: F841
    adult_employed = PersonBuilder(household).gender_female().separated().employed(25000).adult().create_and_write()    # noqa: F841
    adult_unemployed1 = PersonBuilder(household).unemployed().adult().create_and_write()                                # noqa: F841
    adult_unemployed2 = PersonBuilder(household).unemployed().adult().create_and_write()                                # noqa: F841

    return household


@pytest.fixture
def all_families(family1, family2, family3, family4, family5):
    return locals().values()
