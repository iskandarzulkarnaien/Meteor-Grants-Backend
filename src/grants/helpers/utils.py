from grants.models import Household, Person
from sqlalchemy import or_, func
from datetime import date
from dateutil.relativedelta import relativedelta
from functools import reduce


class QueryBuilder():
    def __init__(self):
        # Dictionary of values to lists
        self.query = Household.query

        self.household_types = []
        self.family_member_names = []
        self.num_family_members = []
        self.num_babies = []
        self.num_children = []
        self.num_adults = []
        self.num_elders = []

        self.teenage_students_flag = False
        self.min_num_teenage_students = None
        self.max_num_teenage_students = None

        self.total_annual_income_flag = False
        self.min_total_annual_income = None
        self.max_total_annual_income = None

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

    # TODO: Validate min <= max
    def set_limits_teenage_students(self, limits):
        self.teenage_students_flag = True

        min_num, max_num = int(limits[0]), int(limits[1])
        self.min_num_teenage_students = min_num if min_num else 0
        self.max_num_teenage_students = max_num if max_num else 9999  # Arbitrarily large value. Unlikely that a family will have this many

        return self

    def set_total_annual_income_limits(self, limits):
        self.total_annual_income_flag = True

        min_num, max_num = int(limits[0]), int(limits[1])
        self.min_total_annual_income = min_num if min_num else 0
        self.max_total_annual_income = max_num if max_num else float('inf')
        return self

    def run(self, include_invalid_members=True):
        # Construct query with every param, then run it and return the result
        subqueries = []

        if self.household_types:
            subquery = Household.query.filter(Household.housing_type.in_(self.household_types))
            subqueries.append(subquery)

        if self.family_member_names:
            names_queries = QueryBuilder.generate_or_query(
                lambda name: Household.family_members.any(Person.name.like(f'%{name}%')),
                self.family_member_names
            )
            subquery = Household.query.join(Household.family_members).filter(names_queries)
            subqueries.append(subquery)

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

        if self.teenage_students_flag:
            subquery = Household.query.join(Household.family_members) \
                .filter((Person.date_of_birth >= DateHelper.date_years_ago(16)) & (Person.occupation_type == 'Student')) \
                .group_by(Household).having(
                    (func.count(Person.id) >= int(self.min_num_teenage_students)) &
                    (func.count(Person.id) <= int(self.max_num_teenage_students))
                )
            subqueries.append(subquery)

        if self.total_annual_income_flag:
            subquery = Household.query.filter(
                (Household.total_annual_income >= int(self.min_total_annual_income)) &
                (Household.total_annual_income <= int(self.max_total_annual_income))
            )
            subqueries.append(subquery)

        if self.num_children:
            num_children_queries = QueryBuilder.generate_or_query(
                lambda num: func.count(Person.id) == int(num),
                self.num_children
            )
            self.query = self.query.join(Household.family_members) \
                .filter(Person.date_of_birth > DateHelper.date_years_ago(18)) \
                .group_by(Household).having(num_children_queries)

        if self.num_babies:
            num_babies_queries = QueryBuilder.generate_or_query(
                lambda num: func.count(Person.id) == int(num),
                self.num_babies
            )
            self.query = self.query.join(Household.family_members) \
                .filter(Person.date_of_birth > DateHelper.date_months_ago(8)) \
                .group_by(Household).having(num_babies_queries)

        if subqueries:
            final_query = QueryBuilder.combine_queries(subqueries)
        else:
            final_query = Household.query.all()

        query_results_json = [household.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse']) for household in final_query]

        return query_results_json

    @staticmethod
    def generate_or_query(query_function, items):
        queries = [query_function(item) for item in items]
        return or_(*queries)

    @staticmethod
    def combine_queries(queries):
        def reducer(q1, q2):
            stmt1 = q2.subquery()
            reduced_query = q1.outerjoin(stmt1, Household.id == stmt1.c.id).filter(stmt1.c.id != None)
            return reduced_query

        combined_queries = reduce(reducer, queries)
        return combined_queries


class DateHelper():

    @staticmethod
    def date_years_ago(years):
        return date.today() - relativedelta(years=years)

    @staticmethod
    def date_months_ago(months):
        return date.today() - relativedelta(months=months)

    @staticmethod
    def age_from_dob(date_of_birth):
        age = relativedelta(date.today(), date_of_birth)
        return {
            'years': age.years,
            'months': age.months
        }
