from flask import Blueprint

households = Blueprint('households', __name__)

@households.route('/household/new', methods=['POST'])
def create_household():
    return {}
