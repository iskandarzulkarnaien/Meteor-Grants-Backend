from grants.models import Household


class QueryBuilder():
    def __init__(self):
        # Dictionary of values to lists
        self.query = Household.query
        self.params = {
            'HouseholdTypes': [],
            'FamilyMemberNames': [],
            'NumFamilyMembers': None,
            'NumBaby': None,
            'NumChild': None,
            'NumAdults': None,
            'NumElder': None,
            'NumTeenageStudents': None,
            'MinTotalAnnualIncome': None,
            'MaxTotalAnnualIncome': None
        }

    def household_types(self, housing_types):
        self.params['HouseholdTypes'] = housing_types
        return self

    def run(self, include_invalid_members=True):
        # Construct query with every param, then run it and return the result
        if self.params['HouseholdTypes']:
            valid_household_types = self.params['HouseholdTypes']
            self.query = self.query.filter(Household.housing_type.in_(valid_household_types))

        query_results_json = [household.to_json(excludes=['ID']) for household in self.query]
        return query_results_json
