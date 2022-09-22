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

        self.num_family_members_flag = False
        self.min_num_family_members = None
        self.max_num_family_members = None

        self.num_babies_flag = False
        self.min_num_babies = None
        self.max_num_babies = None

        self.num_children_flag = False
        self.min_num_children = None
        self.max_num_children = None

        self.num_adults_flag = False
        self.min_num_adults = None
        self.max_num_adults = None

        self.num_elders_flag = False
        self.min_num_elders = None
        self.max_num_elders = None

        self.num_teenage_students_flag = False
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

    def set_limits_num_family_members(self, limits):
        self.num_family_members_flag = True

        min_num, max_num = int(limits[0]), int(limits[1])
        self.min_num_family_members = min_num if min_num else 0
        self.max_num_family_members = max_num if max_num else 9999  # Arbitrarily large value. Unlikely that a family will have this many
        return self

    def set_limits_num_babies(self, limits):
        self.num_babies_flag = True

        min_num, max_num = int(limits[0]), int(limits[1])
        self.min_num_babies = min_num if min_num else 0
        self.max_num_babies = max_num if max_num else 9999  # Arbitrarily large value. Unlikely that a family will have this many
        return self

    def set_limits_num_children(self, limits):
        self.num_children_flag = True

        min_num, max_num = int(limits[0]), int(limits[1])
        self.min_num_children = min_num if min_num else 0
        self.max_num_children = max_num if max_num else 9999  # Arbitrarily large value. Unlikely that a family will have this many
        return self

    def set_limits_num_adults(self, limits):
        self.num_adults_flag = True

        min_num, max_num = int(limits[0]), int(limits[1])
        self.min_num_adults = min_num if min_num else 0
        self.max_num_adults = max_num if max_num else 9999  # Arbitrarily large value. Unlikely that a family will have this many
        return self

    def set_limits_num_elders(self, limits):
        self.num_elders_flag = True

        min_num, max_num = int(limits[0]), int(limits[1])
        self.min_num_elders = min_num if min_num else 0
        self.max_num_elders = max_num if max_num else 9999  # Arbitrarily large value. Unlikely that a family will have this many
        return self

    # TODO: Validate min <= max
    def set_limits_num_teenage_students(self, limits):
        self.num_teenage_students_flag = True

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

        if self.num_family_members_flag:
            subquery = Household.query.join(Household.family_members).group_by(Household).having(
                (func.count(Person.id) >= self.min_num_family_members) &
                (func.count(Person.id) <= self.max_num_family_members)
            )
            subqueries.append(subquery)

        if self.num_adults_flag:
            subquery = Household.query.join(Household.family_members) \
                .filter(
                    (Person.date_of_birth <= DateHelper.date_years_ago(18)) &
                    (Person.date_of_birth >= DateHelper.date_years_ago(55))
                ).group_by(Household) \
                .having(QueryBuilder.num_people_in_range_inclusive_constraint(self.min_num_adults, self.max_num_adults))
            subqueries.append(subquery)

        if self.num_elders_flag:
            subquery = Household.query.join(Household.family_members) \
                .filter(Person.date_of_birth < DateHelper.date_years_ago(55)).group_by(Household) \
                .having(QueryBuilder.num_people_in_range_inclusive_constraint(self.min_num_elders, self.max_num_elders))
            subqueries.append(subquery)

        if self.num_teenage_students_flag:
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

        if self.num_children_flag:
            subquery = Household.query.join(Household.family_members) \
                .filter(Person.date_of_birth > DateHelper.date_years_ago(18)).group_by(Household) \
                .having(QueryBuilder.num_people_in_range_inclusive_constraint(self.min_num_children, self.max_num_children))
            subqueries.append(subquery)

        if self.num_babies_flag:
            subquery = Household.query.join(Household.family_members) \
                .filter(Person.date_of_birth > DateHelper.date_months_ago(8)).group_by(Household) \
                .having(QueryBuilder.num_people_in_range_inclusive_constraint(self.min_num_babies, self.max_num_babies))
            subqueries.append(subquery)

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
    def num_people_in_range_inclusive_constraint(min_num, max_num):
        return (
            (func.count(Person.id) >= int(min_num)) &
            (func.count(Person.id) <= int(max_num))
        )

    @staticmethod
    def combine_queries(queries):
        def reducer(q1, q2):
            stmt1 = q2.subquery()
            # TODO: Investigate whether this lint issue can be fixed without breaking the app. To be done after grants API is fully implemented.
            reduced_query = q1.outerjoin(stmt1, Household.id == stmt1.c.id).filter(stmt1.c.id != None)  # noqa: E711
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
