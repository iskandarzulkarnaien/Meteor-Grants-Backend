from grants import db
from sqlalchemy.orm import validates


class Household(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    housing_type = db.Column(db.String, nullable=False)

    @validates('housing_type')
    def validate_housing_type(self, _, housing_type):
        print(_, housing_type)
        assert housing_type in {'Landed', 'Condominium', 'HDB'}
        return housing_type
