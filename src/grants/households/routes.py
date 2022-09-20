from flask import Blueprint, request
from grants.models import Household, Person
from grants import db
from datetime import datetime

households = Blueprint('households', __name__)


@households.route('/household/new', methods=['POST'])
def create_household():
    housing_type = request.form.get('Housing Type')

    try:
        household = Household(housing_type=housing_type)
    except AssertionError:
        return "Invalid housing type", 400
    db.session.add(household)
    db.session.commit()
    return {}


@households.route('/household/<int:household_id>/family/new', methods=['POST'])
def add_person_to_household(household_id):
    name = request.form.get('Name')
    gender = request.form.get('Gender')
    marital_status = request.form.get('MaritalStatus')
    spouse_id = request.form.get('Spouse')
    occupation_type = request.form.get('OccupationType')
    annual_income = request.form.get('AnnualIncome')

    date_of_birth_str = request.form.get('DOB')
    date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d')

    try:
        person = Person(name=name, gender=gender, marital_status=marital_status, spouse_id=spouse_id, occupation_type=occupation_type,
                        annual_income=annual_income, date_of_birth=date_of_birth, household_id=household_id)
    except AssertionError as e:
        return str(e), 400
    db.session.add(person)
    db.session.commit()
    return {}
