from .globalfile import login_required
from app import Blueprint, render_template

usermap = Blueprint('usermap', __name__)

@usermap.route('/map')
@login_required
def locationMap():
	pagetitle = 'Map'
	return render_template('usermap/map.html',pagetitle = pagetitle)
