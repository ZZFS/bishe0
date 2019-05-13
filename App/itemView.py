from flask import Blueprint, render_template

item = Blueprint('item', __name__)


@item.route('/detail')
def find_detail():
    return render_template('detail.html')
