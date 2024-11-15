from app import app, db

class File(db.Model):
    file_id = db.Column(db.UUID(), primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    file_ext = db.Column(db.String(5), nullable=False)
    file_mime = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.BigInteger(), nullable=False)
    user_id = db.Column(db.UUID(), db.ForeignKey('user.uid'), nullable=False)
    org_id = db.Column(db.String(40), db.ForeignKey('org.oid'), nullable=False)
    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

with app.app_context():
    db.create_all()