from flask import Blueprint, request
from grants.models import Household
from grants import db

households = Blueprint('households', __name__)

@households.route('/household/new', methods=['POST'])
def create_household():
    housing_type = request.form.get('Housing Type')
    
    household = Household(housing_type=housing_type)
    db.session.add(household)
    db.session.commit()
    return {}
