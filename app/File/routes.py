from flask import Blueprint, session, request, send_file

import os
import time
import uuid
from loguru import logger
import filetype
import mimetypes
import io
import traceback

from sqlalchemy import and_

from .mimetype import mimetype as mime
from ..File import File
from ..User import User, Org
from app import db

from .Engine.docx import docx_process as docx
from .Engine.txt import text_process as txt
from .Engine.xlsx import sheet_process as xlsx

file = Blueprint('file', __name__)

# target_path = os.path.join(os.path.abspath('.'),'data')
target_path = './data'
if not os.path.exists(target_path):
    os.mkdir('./data')

@file.route('/', methods=['GET'])
def main():
    return {
        'code':0,
        'errno':0,
        'msg': "FILE_MANAGER_API_STATUS_OK"
    }

@file.route('/upload',methods=['POST'])
def upload():
    file = request.files.get('file')
    file_name = file.filename
    file_content = file.stream.read()
    file_guess = filetype.guess(file_content)
    file_type = str()
    if file_guess:
        file_type = file_guess.mime
    elif mimetypes.types_map.get('.'+file_name.split('.')[-1]):
        file_type = mimetypes.types_map.get('.'+file_name.split('.')[-1])
    else:
        return {
            'code': 10,
            'errno': 10,
            'msg': 'UNRECOGNIZABLE_FILE_TYPE'
        }, 403
    file_ext = mimetypes.guess_extension(file_type)[1:]
    file_size = len(file_content)
    file.stream.seek(0)
    user_id = session.get('token').split('|')[1]
    org_id = session.get('token').split('|')[2]
    if not file_type in mime :
        return {
            'code': -10,
            'errno': -10,
            'msg': 'INVALID_DOCUMENT_FILE'
        }, 403
    file_id = uuid.uuid4()
    new_file = File(
        file_id=file_id,
        file_name=file_name,
        file_ext=file_ext,
        file_mime=file_type,
        file_size=file_size,
        user_id=user_id,
        org_id=org_id
    )
    file.save(target_path+'/'+str(file_id)+'.'+file_ext)
    db.session.add(new_file)
    db.session.commit()
    return {
        'code': 0,
        'errno': 0,
        'msg': 'UPLOAD_SUCCESS',
        'data': {
            'file_id': file_id,
            'file_name': file_name,
        }
    }

@file.route('/getList', methods=['POST'])
def fileList():
    query = request.json
    search = query.get('name')
    current = query.get('current')
    size = query.get('size')
    user_id = session.get('token').split('|')[1]
    org_id = session.get('token').split('|')[2]
    if search:
        file_query = File.query.filter(and_(and_(File.user_id==user_id, File.file_name.like("%{}%".format(search))), File.org_id == org_id))
    else:
        file_query = File.query.filter(and_(File.user_id==user_id, File.org_id == org_id))
    f_total = file_query.count()
    f_list = file_query.paginate(page=current,per_page=size)
    f_records = []
    for item in f_list:
        f_records.append({
            'file_id': item.file_id,
            'file_name': item.file_name,
            'file_size': item.file_size,
            'user_id': item.user_id,
            'org_id': org_id
        })
    return {
        'pages': current,
        'size': size,
        'records': f_records,
        'total': f_total
    }

@file.route('/remove', methods=['POST'])
def remove():
    try:
        file_id=request.json.get('id')
        user_id = session.get('token').split('|')[1]
        org_id = session.get('token').split('|')[2]
        file = File.query.filter(File.file_id==file_id, File.org_id==Org.query.filter_by(oid=org_id).first().oid, File.user_id==user_id).first()
        file_path = target_path
        file_ext = file.file_ext
        os.remove(file_path + '/' + str(file_id) + '.' + file_ext)
        db.session.delete(file)
        db.session.commit()
        return {
            'code': 0,
            'errno': 0,
            'msg': 'FILE_REMOVED'
        }
    except Exception as e:
        return {
            'code': -1,
            'errno': -1,
            'msg': 'FILE_REMOVE_FAILED',
            'err_reason': traceback.format_exc()
        }, 500

@file.route('/download', methods=['GET'])
def download():
    file_id = request.args.get('id')
    file_data = File.query.filter_by(file_id=file_id).first()
    user = User.query.filter_by(uid=session['token'].split('|')[1]).first()
    org = Org.query.filter_by(oid=user.oid).first()

    if user.uid != file_data.user_id or user.oid != file_data.org_id:
        return {
            'code': 403,
            'errno': 403,
            'msg': 'PERMISSION_DENIED'
        }, 403
    
    file_path = target_path
    file_ext = file_data.file_ext
    file_type = file_data.file_mime
    try:
        with open(file_path + '/' + str(file_id) + '.' + file_ext,'rb') as file:
            engine = globals().get(file_ext)
            if engine:
                original_file = io.BytesIO(file.read())
                new_file = engine(original_file, file_id, user, org)
                return send_file(new_file, mimetype=file_type, download_name=file_id+'.'+file_ext)
            else:
                original_file = io.BytesIO(file.read())
                return send_file(original_file, mimetype=file_type, download_name=file_id+'.'+file_ext)
    except Exception as e:
        return {
            'code': 500,
            'errno': 500,
            'msg': "FILE_DUMP_FAILED",
            'err_reason': traceback.format_exc()
        }, 500

@file.route('/support_types')
def supportWhat():
    return {
        'code': 0,
        'errno': 0,
        'data': mime
    }, 200

@file.before_request
def interceptor():
    token = session.get('token')
    if token:
        if int(token.split('|')[0]) + (86400 * 3) < (int(time.time())):
            session.pop('token')
            return {
                'code': 403,
                'errno': 403,
                'msg': 'EXPIRED_SESSION'
            }, 403
        else:
            pass
    else:
        return {
            'code': 403,
            'errno': 403,
            'msg': 'INVALID_SESSION'
        }, 403