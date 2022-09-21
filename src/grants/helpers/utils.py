from grants.models import Household


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

        query_results_json = [household.to_json(excludes=['ID'], family_excludes=['ID', 'Spouse']) for household in self.query]
        return query_results_json
