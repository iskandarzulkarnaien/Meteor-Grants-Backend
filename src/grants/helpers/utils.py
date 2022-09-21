from grants.models import Household, Person
from sqlalchemy import or_, func
from datetime import date
from dateutil.relativedelta import relativedelta


class QueryBuilder():
    def __init__(self):
        # Dictionary of values to lists
        self.query = Household.query

        self.household_types = []
        self.family_member_names = []
        self.num_family_members = None
        self.num_babies = None
        self.num_children = None
        self.num_adults = None
        self.num_elders = None
        self.num_teenage_students = None
        self.min_family_annual_income = None
        self.max_family_annual_income = None

    def set_household_types(self, housing_types):
        self.household_types = housing_types
        return self

    def set_family_member_names(self, names):
        self.family_member_names = names
        return self

    def set_num_family_members(self, num):
        self.num_family_members = num
        return self

    def set_num_babies(self, num):
        self.num_babies = num
        return self

    def set_num_children(self, num):
        self.num_children = num
        return self

    def set_num_adults(self, num):
        self.num_adults = num
        return self

    def set_num_elders(self, num):
        self.num_elders = num
        return self

    def set_num_teenage_students(self, num):
        self.num_teenage_students = num
        return self

    def set_total_annual_income(self, min_income=None, max_income=None):
        if min_income is not None:
            self.min_family_annual_income = min_income
        if max_income is not None:
            self.max_family_annual_income = max_income
        return self

    def run(self, include_invalid_members=True):
        # Construct query with every param, then run it and return the result
        if self.household_types:
            self.query = self.query.filter(Household.housing_type.in_(self.household_types))

        if self.family_member_names:
            names_queries = QueryBuilder.generate_or_query(
                lambda name: Household.family_members.any(Person.name.like(f'%{name}%')),
                self.family_member_names
            )
            self.query = self.query.join(Household.family_members).filter(names_queries)

        if self.num_family_members:
            num_family_members_queries = QueryBuilder.generate_or_query(
                lambda num: func.count(Person.id) == int(num),
                self.num_family_members
            )
            self.query = self.query.join(Household.family_members).group_by(Household).having(num_family_members_queries)

        if self.num_adults:
            num_adults_queries = QueryBuilder.generate_or_query(
                lambda num: func.count(Person.id) == int(num),
                self.num_adults
            )
            self.query = self.query.join(Household.family_members) \
                .filter((Person.date_of_birth <= DateHelper.date_years_ago(18)) & (Person.date_of_birth >= DateHelper.date_years_ago(55))) \
                .group_by(Household).having(num_adults_queries)

        if self.num_elders:
            num_elders_queries = QueryBuilder.generate_or_query(
                lambda num: func.count(Person.id) == int(num),
                self.num_elders
            )
            self.query = self.query.join(Household.family_members) \
                .filter(Person.date_of_birth < DateHelper.date_years_ago(55)) \
                .group_by(Household).having(num_elders_queries)

        if self.num_teenage_students:
            num_teenage_students_queries = QueryBuilder.generate_or_query(
                lambda num: func.count(Person.id) == int(num),
                self.num_teenage_students
            )
            self.query = self.query.join(Household.family_members) \
                .filter((Person.date_of_birth >= DateHelper.date_years_ago(16)) & (Person.occupation_type == 'Student')) \
                .group_by(Household).having(num_teenage_students_queries)

        query_results_json = [household.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse']) for household in self.query]
        return query_results_json

    @staticmethod
    def generate_or_query(query_function, items):
        queries = [query_function(item) for item in items]
        return or_(*queries)


class DateHelper():

    @staticmethod
    def date_years_ago(years):
        return date.today() - relativedelta(years=years)

    @staticmethod
    def age_from_dob(date_of_birth):
        age = relativedelta(date.today(), date_of_birth)
        return {
            'years': age.years,
            'months': age.months
        }
