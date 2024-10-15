from flask import Blueprint, render_template

bp = Blueprint('main', __name__)
# Renderização da pagina HTML (FRONTEND)
@bp.route('/')
def index():
    return render_template('index.html')
