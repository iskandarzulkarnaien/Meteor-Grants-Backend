from grants import db
import pytest
from grants.models import Household, Person
from datetime import datetime, timedelta
from flask import url_for
import json
from helpers.utils import PersonBuilder


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
def test_add_person_to_household_success(client, empty_household_saved, person):
    data = person.to_json()

    response = client.post(url_for('households.add_person_to_household', household_id=empty_household_saved.id), data=data)
    assert response.status_code == 200

    # Test that family member has been created
    family_member = Person.query.filter_by(name=person.name).first()
    assert family_member is not None

    # Test that household has the created family member
    db.session.refresh(empty_household_saved)
    household_family_member = empty_household_saved.family_members[0]
    assert family_member is household_family_member


def test_add_person_to_household_wrong_household_does_not_exist(client, empty_household, person):
    data = person.to_json()

    # Route hard-coded as url_for does not allow for non-existent household's id
    response = client.post(f'/household/{empty_household.id}/family/new', data=data)
    assert response.status_code == 404

    family_member = Person.query.filter_by(name=person.name).first()
    assert family_member is None


def test_add_person_to_household_wrong_gender(client, empty_household_saved, person):
    data = person.to_json()
    data['Gender'] = ''

    response = client.post(url_for('households.add_person_to_household', household_id=empty_household_saved.id), data=data)
    assert response.status_code == 400

    family_member = Person.query.filter_by(name=person.name).first()
    assert family_member is None


def test_add_person_to_household_wrong_marital_status(client, empty_household_saved, person):
    data = person.to_json()
    data['MaritalStatus'] = 'Its complicated'

    response = client.post(url_for('households.add_person_to_household', household_id=empty_household_saved.id), data=data)
    assert response.status_code == 400

    family_member = Person.query.filter_by(name=person.name).first()
    assert family_member is None


def test_add_person_to_household_wrong_occupation_type(client, empty_household_saved, person):
    data = person.to_json()
    data['OccupationType'] = 'Black Market Activity'

    response = client.post(url_for('households.add_person_to_household', household_id=empty_household_saved.id), data=data)
    assert response.status_code == 400

    family_member = Person.query.filter_by(name=person.name).first()
    assert family_member is None


def test_add_person_to_household_wrong_future_dated_date_of_birth(client, empty_household_saved, person):
    data = person.to_json()
    tomorrow = (datetime.today() + timedelta(days=1)).date()
    data['DOB'] = tomorrow

    response = client.post(url_for('households.add_person_to_household', household_id=empty_household_saved.id), data=data)
    assert response.status_code == 400

    family_member = Person.query.filter_by(name=person.name).first()
    assert family_member is None


# Tests for API 3
def test_list_all_households_success_no_households(client):
    response = client.get(url_for('households.all_households'))
    assert response.status_code == 200

    # Check the data to see if it tallies with data retrieved from database
    received_households_json = json.loads(response.get_data())
    database_households_json = [household.to_json(excludes=['ID']) for household in Household.query.all()]

    assert received_households_json == database_households_json


def test_list_all_households_success_one_household(client, family1):
    response = client.get(url_for('households.all_households'))
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())
    database_households_json = [household.to_json(excludes=['ID']) for household in Household.query.all()]

    assert received_households_json == database_households_json


def test_list_all_households_success_multiple_households(client, family1, family2, family3):
    response = client.get(url_for('households.all_households'))
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())
    database_households_json = [household.to_json(excludes=['ID']) for household in Household.query.all()]

    assert received_households_json == database_households_json


'''
TODO: Rename all tests to follow convention 'test_<endpoint name>_<test scenario>_<success or fail>
TODO: Mock the expected results where possible instead of using the same code used by the endpoint being tested to pull data,
      since both will return the same results but both results will be wrong.
'''


# Tests for API 4
def test_search_for_household_by_no_params_return_all_success(client, all_families):
    data = {}
    response = client.post(url_for('households.search_households'), data=data)
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())
    expected_households_json = [household.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse']) for household in Household.query.all()]

    assert received_households_json == expected_households_json


@pytest.mark.parametrize('housing_type', Household.valid_housing_types())
def test_search_for_household_by_household_type_success(client, all_families, housing_type):
    data = {
        'HouseholdTypes': [housing_type]
    }
    response = client.post(url_for('households.search_households'), data=data)
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())
    expected_households_json = [household.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse'])
                                for household in Household.query.filter_by(housing_type=housing_type)]

    assert received_households_json == expected_households_json


def test_search_for_household_by_household_type_multiple_types_success(client, all_families):
    data = {
        'HouseholdTypes': ['HDB', 'Landed']
    }
    response = client.post(url_for('households.search_households'), data=data)
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())
    expected_households_json = [household.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse'])
                                for household in Household.query.filter(Household.housing_type.in_(['HDB', 'Landed']))]

    assert received_households_json == expected_households_json


def test_search_for_household_by_family_member_name_success(client, all_families, family1):
    data = {
        # Note: Names intentionally appended with '-123' to make them unique (i.e. unable to be generated by faker) for testing purposes
        'FamilyMemberNames': ['Alice-123']
    }
    response = client.post(url_for('households.search_households'), data=data)
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())

    expected_households = [family1]
    expected_households_json = [family.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse']) for family in expected_households]

    assert received_households_json == expected_households_json


def test_search_for_household_by_family_member_name_multiple_names_success(client, all_families, family1, family2):
    data = {
        'FamilyMemberNames': ['Alice-123', 'Cody-123']
    }
    response = client.post(url_for('households.search_households'), data=data)
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())

    expected_households = [family1, family2]
    expected_households_json = [family.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse']) for family in expected_households]

    assert received_households_json == expected_households_json


def test_search_for_household_by_num_family_members_success(client, all_families, family3, family4, family7):
    data = {
        'FamilyMembersLimits': [5, 6]
    }
    response = client.post(url_for('households.search_households'), data=data)
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())

    expected_households = [family3, family4, family7]
    expected_households_json = [family.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse']) for family in expected_households]

    assert received_households_json == expected_households_json


def test_search_for_household_by_num_baby_success(client, all_families, family6):
    data = {
        'NumBabiesLimits': [0, 1]
    }
    response = client.post(url_for('households.search_households'), data=data)
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())

    expected_households = [family6]
    expected_households_json = [family.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse']) for family in expected_households]

    assert received_households_json == expected_households_json


def test_search_for_household_by_num_children_success(client, all_families, family1, family3, family4, family8):
    data = {
        'NumChildrenLimits': [2, 3]
    }
    response = client.post(url_for('households.search_households'), data=data)
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())

    expected_households = [family1, family3, family4, family8]
    expected_households_json = [family.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse']) for family in expected_households]

    assert received_households_json == expected_households_json


def test_search_for_household_by_num_adults_success(client, all_families, family2, family5):
    data = {
        'NumAdultsLimits': [3, 4]
    }
    response = client.post(url_for('households.search_households'), data=data)
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())

    expected_households = [family2, family5]
    expected_households_json = [family.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse']) for family in expected_households]

    assert received_households_json == expected_households_json


def test_search_for_household_by_num_elders_success(client, all_families, family4):
    data = {
        'NumEldersLimits': [2, 2]
    }
    response = client.post(url_for('households.search_households'), data=data)
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())

    expected_households = [family4]
    expected_households_json = [family.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse']) for family in expected_households]

    assert received_households_json == expected_households_json



def test_search_for_household_by_num_teenage_students_success(client, all_families, family1, family8):
    data = {
        'NumTeenageStudentsLimits': [2, 2]
    }
    response = client.post(url_for('households.search_households'), data=data)
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())

    expected_households = [family1, family8]
    expected_households_json = [family.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse']) for family in expected_households]

    assert received_households_json == expected_households_json


def test_search_for_household_by_total_annual_income_success(client, all_families, family4, family5):
    data = {
        'TotalAnnualIncomeLimits': [20000, 30000]
    }
    response = client.post(url_for('households.search_households'), data=data)
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())

    expected_households = [family4, family5]
    expected_households_json = [family.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse']) for family in expected_households]

    assert received_households_json == expected_households_json


'''
Tests for API 4 & 5

Note: API 5 is essentially a restricted version of API 4, which returns only the valid family members rather than the entire household

Therefore, we can use these tests to check that API 4 correctly returns valid households when passed multiple search parameters
(in the form of the various grant criteria)

These tests can also be used to check API 5 by passing a flag to indicate to return only the valid family members
'''


def test_search_for_household_by_student_encouragement_bonus_entire_household_success(client, all_families, family1, family2):
    data = {
        'NumTeenageStudentsLimits': [1, 0],
        'TotalAnnualIncomeLimits': [0, 200000]
    }
    response = client.post(url_for('households.search_households'), data=data)
    assert response.status_code == 200

    received_households_json = json.loads(response.get_data())

    expected_households = [family1, family2]
    expected_households_json = [family.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse']) for family in expected_households]

    assert received_households_json == expected_households_json

# def test_search_for_household_by_student_encouragement_bonus_success(client, all_families):
#     pass


# def test_search_for_household_by_multigeneration_scheme_success(client, all_families):
#     pass


# def test_search_for_household_by_elder_bonus_success(client, all_families):
#     pass


# def test_search_for_household_by_baby_sunshine_grant_success(client, all_families):
#     pass


# def test_search_for_household_by_yolo_gst_grant_success(client, all_families):
#     pass


# Other Tests: Tests for spouse-to-spouse relationship
def test_spouse_to_spouse_in_PersonBuilder(client, empty_household_saved):
    alice = PersonBuilder(empty_household_saved).name('Alice').gender_female().married().adult().employed().create_and_write()
    bob = PersonBuilder(empty_household_saved).name('Bob').gender_male().married(spouse=alice).adult().employed().create_and_write()

    alice = Person.query.filter_by(name='Alice').first()

    assert alice.spouse_id == bob.id
    assert bob.spouse_id == alice.id


def test_spouse_to_spouse_in_add_person_to_household_endpoint(client, empty_household_saved):
    alice = PersonBuilder(empty_household_saved).name('Alice').gender_female().married().adult().employed().create()
    response = client.post(url_for('households.add_person_to_household', household_id=empty_household_saved.id), data=alice.to_json())
    assert response.status_code == 200

    saved_alice = Person.query.filter_by(name='Alice').first()

    bob = PersonBuilder(empty_household_saved).name('Bob').gender_male().married(spouse=saved_alice).adult().employed().create()
    response = client.post(url_for('households.add_person_to_household', household_id=empty_household_saved.id), data=bob.to_json())
    assert response.status_code == 200

    saved_bob = Person.query.filter_by(name='Bob').first()

    assert saved_alice.spouse_id == saved_bob.id
    assert saved_bob.spouse_id == saved_alice.id
