from grants import db
from grants.models import Person
from faker import Faker
from random import shuffle


class PersonBuilder():
    def __init__(self, household):
        self.household = household

        self.person = Person()
        self.person.household_id = household.id

        self.fake = Faker()
        Faker.seed('123')

    @staticmethod
    def create_generic_person():
        pass

    # Gender Related
    def gender_male(self):
        pass

    def gender_female(self):
        pass

    def gender_invalid(self):
        pass

    # Marital Status Related
    def marital_status(self, spouse=None):
        pass

    # Occupation Type Related
    def unemployed(self):
        pass

    def student(self):
        pass

    def employed(self):
        pass

    # Annual Income Related
    def annual_income(self, lower_bound=None, upper_bound=None):
        pass

    # Age Related
    def baby(self):
        pass

    def teenager(self):
        pass

    def adult(self):
        pass

    def elder(self):
        pass

    def create(self):
        self.person.name = self.fake.name()

        if not self.person.gender:
            self.person.gender = Utils.get_random(Person.valid_genders())

        if not self.person.marital_status:
            self.person.marital_status = Utils.get_random(Person.valid_marital_statuses())

        # TODO: Spouse behavior

        if not self.person.occupation_type:
            self.person.occupation_type = Utils.get_random(Person.valid_occupation_types())

        if not self.person.annual_income:
            self.person.annual_income = 12000  # TODO: Generate random income here

        if not self.person.date_of_birth:
            self.person.date_of_birth = '1997-08-12'  # TODO: Generate random age here

        return self.person

    def create_and_write(self):
        db.session.add(self.household)

        person = self.create()
        db.session.add(person)
        db.session.commit()

        return person


class Utils():
    # Note: computationally expensive since it has to convert the whole set to a list then random sort it, please use only for small sets
    def get_random(set):
        values = list(set)
        shuffle(values)
        return values.pop()
