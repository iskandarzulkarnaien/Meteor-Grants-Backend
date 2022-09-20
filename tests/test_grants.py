from grants import create_app, db
import pytest
from grants.models import Household, Person


@pytest.fixture
def client():
    app = create_app(True)
    with app.app_context():
        db.create_all()
        with app.test_client() as test_app:
            yield test_app
        db.drop_all()


@pytest.fixture
def household():
    household = Household(housing_type='Landed')
    return household


@pytest.fixture
def person():
    person = Person(
        name='Jonathan Yao',
        gender='M',
        marital_status='Single',
        spouse_id=None,
        occupation_type='Employed',
        annual_income='12000',
        date_of_birth='08-12-1997'
    )
    return person


@pytest.mark.parametrize('housing_type', ['Landed', 'Condominium', 'HDB'])
def test_create_household_success(client, housing_type):
    data = {
        'Housing Type': housing_type
    }
    response = client.post('/household/new', data=data)
    assert response.status_code == 200  # OK

    household = Household.query.get(1)
    assert household.housing_type == housing_type


def test_create_household_wrong_housing_type(client):
    data = {
        'Housing Type': 'Pulau Ubin'
    }
    response = client.post('/household/new', data=data)
    assert response.status_code == 400  # Bad Request

    household = Household.query.filter_by(housing_type='Pulau Ubin').first()
    assert household is None


def test_add_person_to_household_success(client, household, person):
    db.session.add(household)
    db.session.commit()

    data = person.to_json()

    response = client.post(f'/household/{household.id}/family/new', data=data)
    assert response.status_code == 200

    # Test that family member has been created
    family_member = Person.query.filter_by(name=person.name).first()
    assert family_member is not None

    # Test that household has the created family member
    db.session.refresh(household)
    household_family_member = household.family_members[0]
    assert family_member is household_family_member


def test_add_person_to_household_wrong_gender(client, household, person):
    db.session.add(household)
    db.session.commit()

    data = person.to_json()
    data['Gender'] = ''

    response = client.post(f'/household/{household.id}/family/new', data=data)
    assert response.status_code == 400

    family_member = Person.query.filter_by(name=person.name).first()
    assert family_member is None

def test_add_person_to_household_wrong_marital_status(client, household, person):
    db.session.add(household)
    db.session.commit()

    data = person.to_json()
    data['MaritalStatus'] = 'Its complicated'

    response = client.post(f'/household/{household.id}/family/new', data=data)
    assert response.status_code == 400

    family_member = Person.query.filter_by(name=person.name).first()
    assert family_member is None
