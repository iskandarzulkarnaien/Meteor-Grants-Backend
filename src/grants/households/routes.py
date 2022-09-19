from flask import Blueprint, request
from grants.models import Household
from grants import db

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
