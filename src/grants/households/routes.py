from flask import Blueprint, request
from grants.models import Household, Person
from grants import db
from grants.helpers.utils import QueryBuilder

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
    date_of_birth = request.form.get('DOB')

    try:
        person = Person(name=name, gender=gender, marital_status=marital_status, spouse_id=spouse_id, occupation_type=occupation_type,
                        annual_income=annual_income, date_of_birth=date_of_birth, household_id=household_id)
    except AssertionError as e:
        return str(e), 400

    db.session.add(person)
    db.session.commit()
    if spouse_id:
        spouse = Person.query.get(spouse_id)
        spouse.spouse_id = person.id
        db.session.commit()
    return {}


@households.route('/household/all')
def all_households():
    return [household.to_json(excludes=['ID']) for household in Household.query.all()]


@households.route('/household/search', methods=['POST'])
def search_households():
    query = handle_search_query(request)
    return query.run()


@households.route('/household/search/grants', methods=['POST'])
def search_households_grants():
    query = handle_search_query(request)
    grant_type = request.form.get('GrantType')
    return query.run(grant=grant_type)


# Helpers
def handle_search_query(request):
    query = QueryBuilder()

    household_types = request.form.getlist('HouseholdTypes')
    if household_types:
        query.set_household_types(household_types)

    family_member_names = request.form.getlist('FamilyMemberNames')
    if family_member_names:
        query.set_family_member_names(family_member_names)

    family_members_limits = request.form.getlist('FamilyMembersLimits')
    if family_members_limits:
        query.set_limits_num_family_members(family_members_limits)

    num_adults_limits = request.form.getlist('NumAdultsLimits')
    if num_adults_limits:
        query.set_limits_num_adults(num_adults_limits)

    num_elders_limits = request.form.getlist('NumEldersLimits')
    if num_elders_limits:
        query.set_limits_num_elders(num_elders_limits)

    num_teenage_students_limits = request.form.getlist('NumTeenageStudentsLimits')
    if num_teenage_students_limits:
        query.set_limits_num_teenage_students(num_teenage_students_limits)

    total_annual_income_limits = request.form.getlist('TotalAnnualIncomeLimits')
    if total_annual_income_limits:
        query.set_total_annual_income_limits(total_annual_income_limits)

    num_children_limits = request.form.getlist('NumChildrenLimits')
    if num_children_limits:
        query.set_limits_num_children(num_children_limits)

    num_babies_limits = request.form.getlist('NumBabiesLimits')
    if num_babies_limits:
        query.set_limits_num_babies(num_babies_limits)
    return query
