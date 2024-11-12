from flask import Blueprint, jsonify
from ..services import pipefy_service

bp = Blueprint('status', __name__, url_prefix='/status')

# STATUS DA API (SEM LIMITE)

@bp.route('/all-cards', methods=['GET'])
def all_cards():
    cards_data = pipefy_service.get_all_cards()
    return jsonify(cards_data)