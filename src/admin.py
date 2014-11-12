from flask import Blueprint
from flask import g, session, request, redirect, url_for
from flask import render_template
from Forms import searchForm, AdminEdit


admin = Blueprint('admin',__name__,template_folder='templates')


def getComplaintData(status):
	if status == "all":
		g.database.execute("SELECT * FROM complaints")
	elif status == "pending":
		g.database.execute("SELECT * FROM complaints WHERE Action_by_admin IS NULL")
	else:
		g.database.execute("SELECT * FROM complaints WHERE Action_by_admin IS NOT NULL")

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
		g.database.execute("SELECT Username FROM entries WHERE User_id=%s" % (complaint[5]))
		data['complainteeid'] = complaint[5]
		data['complaintee'] = g.database.fetchone()[0]
		g.database.execute("SELECT User_id FROM comments WHERE Comment_id=%s" % (complaint[4]))
		data['defendantid'] = g.database.fetchone()[0]

		g.database.execute("SELECT Username FROM entries WHERE User_id=%s" % (data['defendantid']))
		data['defendantname'] = g.database.fetchone()[0]
		retval.append(data)

	return retval


@admin.route('/admin/<userid>/<status>/')
def adminPage(userid, status):
	complaints = getComplaintData(status)
	return render_template('adminpage/index.html',
							complaints=complaints, 
							form6 = searchForm(prefix='form6'),
							adminform = AdminEdit())


@admin.route('/admin/addremark/<complaintid>', methods=["POST"])
def addremark(complaintid):
	g.database.execute("UPDATE complaints SET Action_by_admin=%s WHERE Complain_id=%s" % (request.form['remove'], complaintid))
	g.conn.commit()

	if request.form['remove'] == '1':
		g.database.execute("""SELECT Comment_id FROM complaints WHERE Complain_id=%s""" % (complaintid))
		commentid = g.database.fetchone()[0]

		g.database.execute("""DELETE FROM comments WHERE Comment_id=%s""" % (commentid))
		g.conn.commit()

	if request.form['remarks'] != None:
		g.database.execute("""UPDATE complaints SET remarks="%s" WHERE Complain_id=%s """ % (request.form['remarks'], complaintid))
		g.conn.commit()

	return redirect(url_for('admin.adminPage', userid= session['userid']))		