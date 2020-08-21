# to run:
# export FLASK_APP=api.py
# flask run
from enum import Enum
from flask import Flask, jsonify, request, send_file
from flask_api import status
from my_flask_ldap_auth import login_required, token, User
from ldap3 import Server,Connection,Reader,ObjectDef, ALL
from werkzeug.utils import secure_filename
import base64
import json
import ntpath
import os
import subprocess
import tempfile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'somethingsecret' # TODO config
app.config['LDAP_AUTH_SERVER'] = 'ldap://ipa.demo1.freeipa.org' # TODO config
app.config['LDAP_TOP_DN'] = 'cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org' # TODO config
app.register_blueprint(token, url_prefix='/auth')
app.debug = True # TODO config

RABE = "rabe-debug" # TODO config

STRING = 'STRING'
FILE = 'FILE'

class Default:
    def __init__(self, error_msg):
        self.error_msg = str(error_msg)

    def encrypt(self):
        return {
            'error': self.error_msg
        }

    def decrypt(self):
        return {
            'error': self.error_msg
        }

class StringCryptor(Default):
    def encrypt(self, request) -> str:
        content = request.json
        pt = content['pt'].replace('"', '\\"')
        policy = json.dumps(content['policy']).replace('"', '\\"')

        if len(pt) > 125000: # TODO automatically switch to file-encryption
            return {
                'error': 'String too long, use filetype encryption ("type": "file")'
            }

        cmd="./{rabe} --scheme BSW encrypt --input \"{pt}\" --policy \"{policy}\"" # TODO convert to C bindings
        result = subprocess.check_output(cmd.format(rabe = RABE, pt = pt, policy = policy), shell=True)

        return {
            'ct': result.decode("utf-8")
        }

    def decrypt(self, request) -> str:
        try:
            content = request.json
            ct = content['ct'].replace('"', '\\"')
            atts = User.get(request).get_attributes()

            if len(ct) > 125000: # TODO automatically switch to file-encryption
                return {
                    'error': 'String too long, use filetype encryption ("type": "file")'
                }

            # SHOULDBE: ❯ ./rabe-debug --scheme BSW keygen --attribute\(s\) "[\"att01\"]"
            cmd="./{rabe} --scheme BSW keygen --attribute\\(s\\) \"{atts}\"" # TODO convert to C bindings
            result = subprocess.check_output(cmd.format(rabe = RABE, atts = " ".join(atts)), shell=True)

            f = tempfile.NamedTemporaryFile()
            f.write(result)

            cmd="./{rabe} --scheme BSW decrypt --public\\ key pk.rkey --input \"{ct}\" --secret\\ key {sk}" # TODO convert to C bindings
            result = subprocess.check_output(cmd.format(rabe = RABE, ct = ct, sk = f.name), shell=True)

            return {
                'pt': result.decode("utf-8")
            }
        except Exception:
            return {
                'error': 'decryption failed'
            }

class FileCryptor(Default):
    def encrypt(self, request) -> str:
        pt_file = request.files['file']
        policy = request.form.get('policy')

        if 'file' not in request.files:
            return {
                'error': 'no file in request'
            }

        if pt_file.filename == '':
            return {
                'error': 'file has no filename'
            }

        tempdirpath = tempfile.mkdtemp()
        filename = secure_filename(pt_file.filename)
        pt_file.save(os.path.join(tempdirpath, filename))

        cmd="./{rabe} --scheme BSW encrypt --file \"{filepath}\" --policy {policy}" # TODO convert to C bindings
        result_file_path = subprocess.check_output(cmd.format(rabe = RABE, filepath = os.path.join(tempdirpath, filename), policy = json.dumps(policy)), shell=True)

        return {
            'download_url': '/'.join([request.url_root, 'download', base64.b64encode(result_file_path).decode("utf-8")]) # TODO should be more secure, now it's just b64'ing the tmp-file-path, which gets decoded upon download, it should make use of a cryptographic timely-secured key
        }

    def decrypt(self, request) -> str:
        try:
            ct_file = request.files['file']
            atts = User.get(request).get_attributes()

            if 'file' not in request.files:
                return {
                    'error': 'no file in request'
                }

            if ct_file.filename == '':
                return {
                    'error': 'file has no filename'
                }

            tempdirpath = tempfile.mkdtemp()
            filename = secure_filename(ct_file.filename)
            ct_file.save(os.path.join(tempdirpath, filename))

            # SHOULDBE: ❯ ./rabe-debug --scheme BSW keygen --attribute\(s\) "[\"att01\"]"
            cmd = "./{rabe} --scheme BSW keygen --attribute\\(s\\) \"{atts}\"" # TODO convert to C bindings
            result = subprocess.check_output(cmd.format(rabe = RABE, atts = " ".join(atts)), shell=True)

            f = tempfile.NamedTemporaryFile()
            f.write(result)

            cmd = "./{rabe} --scheme BSW decrypt --public\\ key pk.rkey --file \"{filepath}\" --secret\\ key {sk}" # TODO convert to C bindings
            result_file_path = subprocess.check_output(cmd.format(rabe = RABE, filepath = os.path.join(tempdirpath, filename), sk = f.name), shell=True)
            return {
                'download_url': '/'.join([request.url_root, 'download', base64.b64encode(result_file_path).decode("utf-8")]) # TODO should be more secure, now it's just b64'ing the tmp-file-path, which gets decoded upon download, it should make use of a cryptographic timely-secured key
            }
        except Exception as e:
            print(e)
            return {
                'error': 'decryption failed'
            }

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def GetCryptor(request) -> Default:
    try:
        if request.json:
            # TODO validate json
            cryptor_type = request.json['type'].upper()
            if cryptor_type == STRING:
                return StringCryptor(request)
            if cryptor_type == FILE:
                return FileCryptor(request)
            return Default('Couldn\'t parse type, use \'string\' or \'file\'')
        if request.files:
            # TODO validate request
            return FileCryptor(request)
        return Default('Couldn\'t parse request, supported types are json and form-data')
    except Exception as e:
        return Default(e)

@app.route('/encrypt', methods=['POST'])
@login_required
def encrypt():
    cryptor = GetCryptor(request)
    return jsonify(cryptor.encrypt(request))

@app.route('/decrypt', methods=['POST'])
@login_required
def decrypt():
    cryptor = GetCryptor(request)
    return jsonify(cryptor.decrypt(request))

@app.route('/download/<string:download_file>', methods=['GET'])
@login_required
def download(download_file):
    try:
        file_path = os.path.normpath(base64.b64decode(download_file)).decode("utf-8")

        if (file_path.startswith('/tmp/') == False):
            return '', status.HTTP_404_NOT_FOUND

        return send_file(file_path, as_attachment=True, attachment_filename=path_leaf(file_path))
    except Exception:
        return '', status.HTTP_404_NOT_FOUND

@app.route('/')
@login_required
def hello():
    user = User.get(request)

    return 'Hello, ' + user.username + '<br/>attributes:<br/>' + '<br/>'.join(user.get_attributes())

# todo persistence
# todo config -> encryption types: orderbijlage, adresboek -> url value?
# todo dockerize
# todo tests, snelheid, dataverbruik
