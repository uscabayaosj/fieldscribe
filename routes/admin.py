from flask import Blueprint, render_template
from flask_login import login_required
from utils.decorators import admin_required

bp = Blueprint('admin', __name__)

@bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')
