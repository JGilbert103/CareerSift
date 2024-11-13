## ADD IMPORTS

## Session verification
@app.route('/')
def index():
        if session.get('user'):
                return render_template("index.html", user=session['user'])

        else:
                return render_template("index.html")

## ADD REGISTER METHOD

## ADD LOGIN METHOD

## Logging out a user
@app.route('/logout')
def logout():
    if session.get('user'):
        session.clear()

    return redirect(url_for('index'))

## IMPLEMENT ADDITIONAL NEEDED METHODS BELOW



## Main Method
if __name__ == "__main__":
    app.run()