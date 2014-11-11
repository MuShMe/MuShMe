from flask import Blueprint
from flask import g, session
from flask import render_template
from Forms import searchForm


admin = Blueprint('admin',__name__,template_folder='templates')


def getComplaintData():
	g.database.execute("SELECT * FROM complaints")
	complaints = g.database.fetchall()
	retval = []

	for complaint in complaints:
		data = {}
		g.database.execute("SELECT Comment FROM comments WHERE Comment_id=%s", complaint[4])
		comment = g.database.fetchone()[0]
		data['comment'] = comment
		data['complainid'] = complaint[0]
		data['type'] = complaint[1]
		data['description'] = complaint[2]
		data['action'] = complaint[3]
		data['complaintee'] = complaint[4]

		retval.append(data)

	return retval


@admin.route('/admin/<userid>')
def adminPage(userid):
	return render_template('adminpage/index.html',complaints=getComplaintData(), form6 = searchForm(prefix='form6'))