from grants import db

class Household(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    housing_type = db.Column(db.String, nullable=False)
