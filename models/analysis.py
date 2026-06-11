from models.user import db

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    incident_text = db.Column(db.Text, nullable=False)
    result = db.Column(db.Text, nullable=False)