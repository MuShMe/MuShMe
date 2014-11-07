from Flask import Blueprint


@app.route('/playlist/<playlistid>')
def playlistPage(playlistid):
    return render_template('playlist/index.html')
