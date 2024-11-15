from app import app, db

class Org(db.Model):
    oid = db.Column(db.String(40), primary_key=True)
    name = db.Column(db.String(100))
    name_eng = db.Column(db.String(200))
    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

class User(db.Model):
    uid = db.Column(db.UUID, primary_key=True, nullable=False)
    username = db.Column(db.String(80), unique=True,nullable=False)
    phone = db.Column(db.String(11), nullable=False)
    pwd = db.Column(db.String(200), nullable=False)
    oid = db.Column(db.String(40), db.ForeignKey('org.oid'))
    avatar = db.Column(db.String(200))
    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

with app.app_context():
    db.create_all()
    if not db.session.query(Org.name).filter(Org.oid == 'XMTORCHT0001').first():
        db.session.add(Org(oid='XMTORCHT0001', name='FJ_厦门火炬高新区测试组织01', name_eng='XM_TorchHT_IDZ_TEST01'))
        db.session.add(Org(oid='XMSPBASET0001', name='FJ_厦门软件园产教融合基地测试01', name_eng='XM_SoftwarePark_PTBASE_TEST01'))
        db.session.commit()