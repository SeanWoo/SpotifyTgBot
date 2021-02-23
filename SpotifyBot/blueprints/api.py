import uuid
from flask import session, request, jsonify
from flask import Blueprint
from extensions import db


api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/callback')
def callback():
    #if not session.get('uuid'):
    #    session['uuid'] = str(uuid.uuid4())
    code = request.args.get("code")

    return jsonify({'error_code': 'ok'})