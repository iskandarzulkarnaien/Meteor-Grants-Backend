from grants import db
from grants.models import Person, Household
from faker import Faker
from random import shuffle, randint
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class PersonBuilder():
    def __init__(self, household):
        self.household = household

        self.person = Person()
        self.person.household_id = household.id

        self.fake = Faker()

    @staticmethod
    def create_generic_person():
        pass

    def name(self, name):
        self.person.name = name
        return self

    # Gender Related
    def gender_male(self):
        self.person.gender = 'M'
        return self

    def gender_female(self):
        self.person.gender = 'F'
        return self

    def gender_invalid(self):
        self.person.gender = ''
        return self

    # Marital Status Related
    def single(self):
        pass

    def married(self, spouse=None):
        self.person.marital_status = 'Married'
        if spouse:
            self.person.spouse_id = spouse.id
        return self

    def widowed(self, spouse=None):
        self.person.marital_status = 'Widowed'
        return self

    def separated(self, spouse=None):
        self.person.marital_status = 'Separated'
        return self

    def divorced(self, spouse=None):
        self.person.marital_status = 'Divorced'
        return self

    def marital_status_not_reported(self):
        self.person.marital_status = 'Not Reported'
        return self

    # Occupation Type Related
    def unemployed(self):
        self.person.occupation_type = 'Unemployed'
        self.person.annual_income = 0
        return self

    def student(self):
        self.person.occupation_type = 'Student'
        self.person.annual_income = 0
        return self

    def employed(self, annual_income=50000):
        self.person.occupation_type = 'Employed'
        self.person.annual_income = annual_income
        return self

    '''
    TODO: Investigate and fix age-related errors.
    Age-related tests sometimes fail when the age are set to the strict limits e.g. (18, 55) for adults.
    Possible off by 1 error or date comparison issue exists.
    '''
    # Age Related
    def baby(self):
        pass

    def teenager(self, age=None):
        if not age:
            age = randint(10, 15)  # Note: start age arbitrarily chosen

        self.person.date_of_birth = Utils.get_date_of_birth_from_age(age)
        return self

    def adult(self, age=None):
        if not age:
            age = randint(19, 54)

        self.person.date_of_birth = Utils.get_date_of_birth_from_age(age)
        return self

    def elder(self, age=None):
        if not age:
            age = randint(57, 99)

        self.person.date_of_birth = Utils.get_date_of_birth_from_age(age)
        return self

    # TODO: Throw exception on failure to provide certain fields.
    def create(self):
        if self.person.gender is None:
            self.person.gender = Utils.get_random(Person.valid_genders())

        # TODO: Generate male and female names respectively
        if self.person.name is None:
            if self.person.gender == 'M':
                self.person.name = self.fake.name()

            if self.person.gender == 'F':
                self.person.name = self.fake.name()

        if not self.person.marital_status:
            self.person.marital_status = 'Single'

        if self.person.occupation_type is None:
            self.person.occupation_type = Utils.get_random(Person.valid_occupation_types())

        if self.person.annual_income is None:
            self.person.annual_income = 12000  # TODO: Generate random income here

        if self.person.date_of_birth is None:
            self.person.date_of_birth = '1997-08-12'  # TODO: Generate random age here

        return self.person

    def create_and_write(self):
        db.session.add(self.household)

        person = self.create()
        db.session.add(person)
        db.session.commit()

        if person.spouse_id:
            spouse = Person.query.get(person.spouse_id)
            spouse.spouse_id = person.id
            db.session.commit()
        return person


class HouseholdBuilder():
    def __init__(self):
        self.household = Household()

    # Household Type related
    def landed(self):
        self.household.housing_type = 'Landed'
        return self

    def condo(self):
        self.household.housing_type = 'Condominium'
        return self

    def hdb(self):
        self.household.housing_type = 'HDB'
        return self

    def add_person(self, person):
        pass

    def create(self):
        if not self.household.housing_type:
            self.household.housing_type = Utils.get_random(Household.valid_housing_types())
        return self.household

    def create_and_write(self):
        household = self.create()

        db.session.add(household)
        db.session.commit()

        for family_member in household.family_members:
            db.session.add(family_member)
        db.session.commit()

        return household


class Utils():
    # Note: computationally expensive since it has to convert the whole set to a list then random sort it, please use only for small sets
    def get_random(set):
        values = list(set)
        shuffle(values)
        return values.pop()

    def get_date_of_birth_from_age(age, years=True):
        # Person could be exactly 1 day from turning age+1 years old
        earliest_birthdate = date.today() - relativedelta(years=age+1) + timedelta(days=1)

        # Person could be exactly age years old
        latest_birthdate = date.today() - relativedelta(years=age)

        days_between_dates = (latest_birthdate - earliest_birthdate).days
        random_number_of_days = randint(0, days_between_dates)

        date_of_birth = earliest_birthdate + timedelta(days=random_number_of_days)
        return date_of_birth
