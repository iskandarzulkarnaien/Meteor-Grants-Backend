from grants import create_app, db
import pytest
from grants.models import Household, Person
from datetime import datetime, timedelta
from flask import url_for
import json
from helpers.utils import PersonBuilder, HouseholdBuilder


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
def household():
    household = HouseholdBuilder().create()
    return household


@pytest.fixture
def person(household):
    person = PersonBuilder(household).create()
    return person


# Tests For API 1
@pytest.mark.parametrize('housing_type', Household.valid_housing_types())
def test_create_household_success(client, housing_type):
    data = {
        'Housing Type': housing_type
    }
    response = client.post(url_for('households.create_household'), data=data)
    assert response.status_code == 200  # OK

    # TODO: Get total number of households and + 1 instead of putting literal 1.
    household = Household.query.get(1)
    assert household.housing_type == housing_type


def test_create_household_wrong_housing_type(client):
    data = {
        'Housing Type': 'Pulau Ubin'
    }
    response = client.post(url_for('households.create_household'), data=data)
    assert response.status_code == 400  # Bad Request

    household = Household.query.filter_by(housing_type='Pulau Ubin').first()
    assert household is None


# Tests for API 2
def test_add_person_to_household_success(client, household, person):
    db.session.add(household)
    db.session.commit()

    data = person.to_json()

    response = client.post(url_for('households.add_person_to_household', household_id=household.id), data=data)
    assert response.status_code == 200

    # Test that family member has been created
    family_member = Person.query.filter_by(name=person.name).first()
    assert family_member is not None

    # Test that household has the created family member
    db.session.refresh(household)
    household_family_member = household.family_members[0]
    assert family_member is household_family_member


def test_add_person_to_household_wrong_household_does_not_exist(client, household, person):
    data = person.to_json()

    # Route hard-coded as url_for does not allow for non-existent household's id
    response = client.post(f'/household/{household.id}/family/new', data=data)
    assert response.status_code == 404

    family_member = Person.query.filter_by(name=person.name).first()
    assert family_member is None


def test_add_person_to_household_wrong_gender(client, household, person):
    db.session.add(household)
    db.session.commit()

    data = person.to_json()
    data['Gender'] = ''

    response = client.post(url_for('households.add_person_to_household', household_id=household.id), data=data)
    assert response.status_code == 400

    family_member = Person.query.filter_by(name=person.name).first()
    assert family_member is None


def test_add_person_to_household_wrong_marital_status(client, household, person):
    db.session.add(household)
    db.session.commit()

    data = person.to_json()
    data['MaritalStatus'] = 'Its complicated'

    response = client.post(url_for('households.add_person_to_household', household_id=household.id), data=data)
    assert response.status_code == 400

    family_member = Person.query.filter_by(name=person.name).first()
    assert family_member is None


def test_add_person_to_household_wrong_occupation_type(client, household, person):
    db.session.add(household)
    db.session.commit()

    data = person.to_json()
    data['OccupationType'] = 'Black Market Activity'

    response = client.post(url_for('households.add_person_to_household', household_id=household.id), data=data)
    assert response.status_code == 400

    family_member = Person.query.filter_by(name=person.name).first()
    assert family_member is None


def test_add_person_to_household_wrong_future_dated_date_of_birth(client, household, person):
    db.session.add(household)
    db.session.commit()

    data = person.to_json()
    tomorrow = (datetime.today() + timedelta(days=1)).date()
    data['DOB'] = tomorrow

    response = client.post(url_for('households.add_person_to_household', household_id=household.id), data=data)
    assert response.status_code == 400

    family_member = Person.query.filter_by(name=person.name).first()
    assert family_member is None


# Tests for API 3
def test_list_all_households_success_no_households(client):
    response = client.get(url_for('households.all_households'))
    assert response.status_code == 200

    # Check the data to see if it tallies with data retrieved from database
    received_households_json = json.loads(response.get_data())
    database_households_json = [household.to_json() for household in Household.query.all()]

    assert received_households_json == database_households_json


def test_list_all_households_success_one_household(client, household, person):
    db.session.add(household)
    db.session.commit()

    person.household_id = household.id
    db.session.add(person)
    db.session.commit()

    response = client.get(url_for('households.all_households'))
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())
    database_households_json = [household.to_json() for household in Household.query.all()]

    assert received_households_json == database_households_json

