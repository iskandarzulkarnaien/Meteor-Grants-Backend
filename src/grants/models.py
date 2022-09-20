from grants import db
from sqlalchemy.orm import validates


class Household(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    housing_type = db.Column(db.String, nullable=False)
    family_members = db.relationship('Person', back_populates='household')

    @validates('housing_type')
    def validate_housing_type(self, _, housing_type):
        assert housing_type in {'Landed', 'Condominium', 'HDB'}
        return housing_type


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    marital_status = db.Column(db.String, nullable=False)

    # TODO: Handle possibility of spouse not existing.
    # Due to limitations of current API (create person one at a time), if we strictly check that the spouse is an already existing person,
    # we will not be able to add any persons with spouses at all.
    # e.g. Alice married to Bob. We cannot add Alice in since Bob is not an existing person. We cannot add Bob since Alice is not an existing person
    spouse_id = db.Column(db.Integer)

    occupation_type = db.Column(db.String, nullable=False)
    annual_income = db.Column(db.Float, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)

    household_id = db.Column(db.Integer, db.ForeignKey('household.id'), nullable=False)
    household = db.relationship('Household', back_populates='family_members')

    @validates('gender')
    def validate_gender(self, _, gender):
        assert gender in {'M', 'F'}
        return gender

    @validates('marital_status')
    def validate_marital_status(self, _, marital_status):
        assert marital_status in {'Single', 'Married', 'Divorced'}
        return marital_status

    def to_json(self):
        return {
            'Name': self.name,
            'Gender': self.gender,
            'MaritalStatus': self.marital_status,
            'Spouse': self.spouse_id,
            'OccupationType': self.occupation_type,
            'AnnualIncome': self.annual_income,
            'DOB': self.date_of_birth,
        }
