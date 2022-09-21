from grants import db
from sqlalchemy.orm import validates
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func, select


class Household(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    housing_type = db.Column(db.String, nullable=False)
    family_members = db.relationship('Person', back_populates='household')

    # Validations

    @validates('housing_type')
    def validate_housing_type(self, _, housing_type):
        assert housing_type in Household.valid_housing_types()
        return housing_type

    # Valid Types

    @staticmethod
    def valid_housing_types():
        return {'Landed', 'Condominium', 'HDB'}

    # Hybrid Properties

    @hybrid_property
    def total_annual_income(self):
        total_annual_income = sum([person.annual_income for person in self.family_members])
        return total_annual_income

    @total_annual_income.expression
    def total_annual_income(cls):
        return (
            select([func.sum(Person.annual_income)])
            .where(Person.household_id == cls.id)
            .label('total_annual_income')
        )

    # Other Methods

    def to_json(self, excludes=[], family_excludes=[]):
        data = {
            'ID': self.id,
            'HouseholdType': self.housing_type,
            'Family Members': [family_member.to_json(excludes=family_excludes) for family_member in self.family_members]
        }
        for item in excludes:
            data.pop(item)
        return data


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    marital_status = db.Column(db.String, nullable=False)

    # TODO: Handle possibility of spouse not existing.
    # Due to limitations of current API (create person one at a time), if we strictly check that the spouse is an already existing person,
    # we will not be able to add any persons with spouses at all.
    # e.g. Alice married to Bob. We cannot add Alice in since Bob is not an existing person. We cannot add Bob since Alice is not an existing person
    spouse_id = db.Column(db.Integer, db.ForeignKey('person.id'))

    occupation_type = db.Column(db.String, nullable=False)
    annual_income = db.Column(db.Float, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)

    household_id = db.Column(db.Integer, db.ForeignKey('household.id'), nullable=False)
    household = db.relationship('Household', back_populates='family_members')

    # Validations

    @validates('gender')
    def validate_gender(self, _, gender):
        assert gender in Person.valid_genders()
        return gender

    @validates('marital_status')
    def validate_marital_status(self, _, marital_status):
        assert marital_status in Person.valid_marital_statuses()
        return marital_status

    @validates('spouse_id')
    def validate_spouse_id(self, _, spouse_id):
        if spouse_id is None:
            return
        spouse = Person.query.get(spouse_id)
        assert spouse is not None
        return spouse_id

    @validates('occupation_type')
    def validate_occupation_type(self, _, occupation_type):
        assert occupation_type in Person.valid_occupation_types()
        return occupation_type

    @validates('date_of_birth')
    def validate_date_of_birth(self, _, date_of_birth):
        if isinstance(date_of_birth, str):
            date_of_birth_converted = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        else:
            date_of_birth_converted = date_of_birth

        assert date_of_birth_converted <= datetime.today().date()
        return date_of_birth_converted

    # Valid Types

    @staticmethod
    def valid_genders():
        return {'M', 'F'}

    @staticmethod
    def valid_marital_statuses():
        return {'Single', 'Married', 'Widowed', 'Separated', 'Divorced', 'Not Reported'}

    @staticmethod
    def valid_occupation_types():
        return {'Unemployed', 'Student', 'Employed'}

    # Other Methods

    def to_json(self, excludes=[]):
        data = {
            'ID': self.id,
            'Name': self.name,
            'Gender': self.gender,
            'MaritalStatus': self.marital_status,
            'Spouse': self.spouse_id,
            'OccupationType': self.occupation_type,
            'AnnualIncome': self.annual_income,
            'DOB': datetime.strftime(self.date_of_birth, '%Y-%m-%d'),
        }
        for item in excludes:
            data.pop(item)
        return data
