from flask import Blueprint, request, session
import hashlib
import uuid
import time
import re
import random
from loguru import logger

from .. import db
from ..User import User, Org
from ..File.re_pattern import pattern_cnphone_full
from app import limiter

from sqlalchemy.exc import IntegrityError

user = Blueprint('user', __name__)

@user.route('/register', methods=['POST'])
def register():
    param = request.json
    username = param.get('username')
    pwd = param.get('pwd')
    phone = param.get('phone')
    validate = param.get('validate')
    oid = param.get('org_id')
    if not re.search('^[a-zA-Z0-9_]{7,25}$',username):
        return {'code': 400,'errno': 400,'msg': "INVALID_USERNAME"}, 400
    elif not re.search('^[a-zA-Z0-9_*#@!&$]{8,20}$',pwd):
        return {'code': 400,'errno': 400,'msg': "INVALID_PASSWORD"}, 400
    elif not re.search(pattern_cnphone_full, str(phone)):
        return {'code': 400,'errno': 400,'msg': "INVALID_PHONE_NUMBER"}, 400
    elif len(validate) != 6:
        return {'code': 400,'errno': 400,'msg': "PHONE_VALIDATE_CODE_REQUIRED"}, 400
    elif not Org.query.filter_by(oid=oid).first():
        return {'code': 400,'errno': 400,'msg': "ORG_PARSE_FAILED"}, 400
    
    sha256_hash = hashlib.sha256()
    sha256_hash.update(str(param['username']).encode('utf-8')+str(param['pwd']).encode('utf-8'))
    pwd = sha256_hash.hexdigest()
    
    sha256_hash_ = hashlib.sha256()
    sha256_hash_.update(str(param['validate']).encode('utf-8'))
    sms_verify_code = sha256_hash_.hexdigest()
    if sms_verify_code != session['sms_verify']:
        return {
            'code': 400,
            'errno': 400,
            'msg': 'SMS_VERIFY_CODE_DISMATCH'
        }, 400

    try: 
        uid = uuid.uuid4()
        new_user = User(uid=uid, username=username, pwd=pwd, avatar='/assets/avatar.png', oid=oid, phone=phone)
        db.session.add(new_user)
        db.session.commit()
        session['sms_verify'] = ''
    except IntegrityError as e:
        return {
            'code': 1,
            'errno': 1,
            'msg': 'REGISTER_VIOLATION',
            'reason': str(e)
        }, 500
    return {
        'code': 0,
        'errno': 0,
        'msg': 'REGISTER_SUCCESS',
        'data': {
            'uid': uid,
            'username': param['username']
        }
    }

@user.route('/login', methods=['POST'])
def login():
    param = request.json
    sha256_hash = hashlib.sha256()
    sha256_hash.update(str(param['username']).encode('utf-8')+str(param['pwd']).encode('utf-8'))
    param['pwd'] = sha256_hash.hexdigest()
    user = db.session.query(User.uid, User.username, User.avatar, User.oid).filter(User.pwd == param['pwd']).first()
    if user:
        org = db.session.query(Org.oid, Org.name, Org.name_eng).filter(Org.oid == user.oid).first()
        session['token'] = str("{}|{}|{}").format(int(time.time()),user.uid,org.oid)
        return {
            'code': 0,
            'errno': 0,
            'data': {
                'uid': user.uid,
                'username': user.username,
                'avatar': user.avatar,
                'org_info': {
                    'org_id': org.oid,
                    'org_name': org.name,
                    'org_name_eng': org.name_eng
                },
                'ip_addr': request.remote_addr or '127.0.0.1'
            },
            'msg': 'success'
        }, 200
    return {
        'code': 400,
        'errno': 400,
        'msg': 'USER_NOT_FOUND'
    }, 400

@user.route('/logout', methods=['DELETE'])
def logout():
    try:
        session.clear()
        return {
            'code': 0,
            'errno': 0,
            'msg': 'LOGOUT_SUCCESS'
        }
    except:
        return {
            'code': -999,
            'errno': -999,
            'msg': "LOGOUT_FAILED"
        }
@user.route('/is_logged', methods=['POST'])
def statusCheck():
    token = session.get('token')
    token = session.get('token')
    if token:
        if int(token.split('|')[0]) > (int(time.time()) + (86400 * 3)):
            session.clear()
            return {
                'code': -403,
                'errno': -403,
                'msg': 'EXPIRED_SESSION'
            }, 401
        else:
            return {
                'code': 0,
                'errno': 0,
                'msg': 'IS_LOGGED'
            },200
    else:
        return {
            'code': 403,
            'errno': 403,
            'msg': 'INVALID_SESSION'
        }, 403

@user.route('/verify', methods=['POST'])
def verify():
    token = session.get('token')
    if token:
        if int(token.split('|')[0]) > (int(time.time()) + (86400 * 3)):
            session.clear()
            return {
                'code': -403,
                'errno': -403,
                'msg': 'EXPIRED_SESSION'
            }, 403
        else:
            user = User.query.filter_by(uid=token.split('|')[1], oid=token.split('|')[2]).first()
            org = Org.query.filter_by(oid=token.split('|')[2]).first()
            if user and org:
                return {
                    'code': 0,
                    'errno': 0,
                    'data': {
                        'uid': user.uid,
                        'username': user.username,
                        'avatar': user.avatar,
                        'org_info': {
                            'org_id': org.oid,
                            'org_name': org.name,
                            'org_name_eng': org.name_eng
                        }
                    },
                    'msg': 'LOGIN_ALREADY'
                }, 200
            else:
                return {                            # Where are you now?
                    'code': 404,                    # Atlantis
                    'errno': 404,                   # Under the C
                    'msg': 'USER_NOT_EXIST'         # Under the C
                }, 404
    else:
        return {
            'code': 403,
            'errno': 403,
            'msg': 'INVALID_SESSION'
        }, 403

@user.route('/org_list')
def getOrgList():
    org_list = Org.query
    org_total = org_list.count()
    org_json = []
    for i in org_list.all():
        org_json.append(i.to_json())
    return {
        'code': 0,
        'errno': 0,
        'data': {
            'total': org_total,
            'orgs': org_json
        }
    }

@user.route('/sms_verify')
@limiter.limit("10 per minute")
def sms_verify():
    phone = request.args.get('phone')
    if phone:
        if not re.search(pattern_cnphone_full, phone):
            return {
                'code': 400,
                'errno': 400,
                'msg': 'INVALID_PHONE_NUMBER'
            }, 400
    else:
        return {
            'code': 400,
            'errno': 400,
            'msg': 'INVALID_PHONE_NUMBER'
        }, 400
    code = str()
    for i in range(0,6):
        code += str(random.randint(0,9))  # 暂时不接短信平台，假验证码
    session['sms_verify'] = hashlib.sha256(code.encode('utf-8')).hexdigest()
    return {
        'code': 0,
        'errno': 0,
        'data': {
            'sms_verify_code': code  
        }
    }, 200