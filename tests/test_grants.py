from grants import create_app, db
import pytest
from grants.models import Household


@pytest.fixture
def client():
    app = create_app(True)
    with app.app_context():
        db.create_all()
        with app.test_client() as test_app:
            yield test_app
        db.drop_all()


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
