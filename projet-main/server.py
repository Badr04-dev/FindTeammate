from flask import Flask, session, render_template, redirect, url_for, request, abort
import data_model as model
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import create_db

app = Flask(__name__)

########################################
# Routes des pages principales du site #
########################################

# Test si l'utilisateur est connecte
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not('username' in session):
            return abort(401)
        else:
            return f(*args, **kwargs)
    return decorated_function


@app.get('/')
def home():
    logged_in = session.get('logged_in', False)
    username = session.get('username', None)

    return render_template('index.html', logged_in=logged_in, username=username)

########################################################


######## Route Pour les nouveaux utilisateurs #########

def new_player(firstname, lastname, picture, username, age, email, phone, password, description):
    return create_db.create_new_player(firstname, lastname, picture, username, age, email, phone, password, description)


@app.get("/new_player")
def get_new_player():
    error=False
    return render_template("new_player.html",error=error)


@app.post('/new_player')
def post_new_player():
    username=request.form["username"]
    password = request.form["password"]
    firstname=request.form["firstname"]
    lastname=request.form["lastname"]
    picture=request.form["picture"]
    age=request.form["age"]
    email=request.form["email"]
    phone=request.form["phone"]
    description=request.form["description"]
    player_id=new_player(firstname, lastname, picture, username, age, email, phone, password, description)
    if player_id==-1:
        error=True
        return render_template("new_player.html",error=error)
    session["username"] = username
    session['id']=player_id
    session['logged_in']=True
    return redirect('/')

########################################################


######## Route se connecter/deconnecter ################

def login(username, password):
    player = model.get_player_by_username(username)

    if player==-1:
        return -2
    password = check_password_hash(player['password'], password)
    if not password:
        return -1

    return player['id']


@app.get('/login')
def login_get():
    session.get('printError', False)
    return render_template("login.html")


@app.post("/login")
def login_post():
    username = request.form["username"]
    password = request.form["password"]

    id = login(username, password)

    if id == -1 or id==-2:
        # Erreur de connexion
        session['printError']=True
        return redirect("/login")

    # Connexion réussie
    session["id"] = id
    session["username"] = username
    session['logged_in']=True
    session['printError']=False
    return redirect('/')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect('/')

########################################################

#################### PLAYER ACCOUNT ####################

@app.get('/player_account/<id>')
@login_required
def get_player_account(id):
    requested_id = int(id)
    if requested_id != session.get('id'):
        abort(403)  # Renvoie une erreur 403 (Forbidden)
    player=model.show_player_account(int(id))
    logged_in=True
    return render_template('player_account.html', player=player,logged_in=logged_in)

@app.get('/update_account/<id>')
@login_required
def get_update_account(id):
    requested_id = int(id)
    if requested_id != session.get('id'):
        abort(403)  # Renvoie une erreur 403 (Forbidden)
    return render_template('update_account.html')

@app.post('/update_account/<id>')
@login_required
def post_update_account(id):
    id=int(id)
    username=request.form["username"]
    password = request.form["password"]
    firstname=request.form["firstname"]
    lastname=request.form["lastname"]
    picture=request.form["picture"]
    age=request.form["age"]
    email=request.form["email"]
    phone=request.form["phone"]
    description=request.form["description"]
    model.update_player_account(id,firstname,lastname,picture,username,age,email,phone,password,description)
    session['username']=username
    return redirect(url_for('get_player_account', id=str(id)))

########################################################

#################### WAITING LIST ####################
@app.get('/waiting_list')
@login_required
def show_waiting_list():
    players = model.show_waiting_list()
    if players is None:
        players = []
    logged_in=True
    return render_template('waiting_list.html', players=players, logged_in=logged_in)

@app.get('/add_to_waiting_list/<id>')
@login_required
def get_add_to_waiting_list(id):
    requested_id = int(id)
    if requested_id != session.get('id'):
        abort(403)  # Renvoie une erreur 403 (Forbidden)
    logged_in=True
    return render_template('add_waiting_list.html',logged_in=logged_in)

@app.route('/add_to_waiting_list/<id>', methods=['POST'])
@login_required
def add_to_waiting_list(id):
    player_id = int(id)
    if player_id != session.get('id'):
        abort(403)
    start = request.form['start']
    end = request.form['end']

    if start>=end:
        session['DateError']=True
        return redirect(url_for('add_to_waiting_list', id=str(id)))

    result = model.add_to_waiting_list(player_id, start, end)
    if result == -1:
        session['printError']=True
        return redirect(url_for('add_to_waiting_list', id=str(id)))
    session['printError']=False
    session['id']=id
    return redirect(url_for('show_waiting_list'))

########################################################

#################### JOIN REQUEST ######################

@app.get('/get_join_request')
@login_required
def get_join_request():
    join_requests = model.get_join_requests_to(session['username'])
    logged_in=True
    return render_template('get_join_request.html', join_requests=join_requests, logged_in=logged_in)

@app.get('/send_request/<username>')
@login_required
def send_join_request(username):
    player=model.get_player_by_username(username)
    if not(model.user_in_waiting_list(player['id'])):
        abort(403)
    logged_in=True
    error2 = False
    error3 = False
    return render_template('send_request.html', player=player, logged_in=logged_in, error3=error3, error2=error2)

@app.post('/send_request/<username>')
@login_required
def post_join_request(username):
    player = model.get_player_by_username(username)
    logged_in = True
    error2 = False
    error3 = False

    requestor_username = session['username']
    requestee_username = username
    message = request.form['message']

    result = model.join_request(requestor_username, requestee_username, message)

    if result == -1:
        abort(403)
    elif result == -2:
        abort(403)
    elif result == -3:
        error2 = True
        return render_template("send_request.html", logged_in=logged_in, error3=error3, error2=error2, player=player)
    elif result == -4:
        error3 = True
        return render_template("send_request.html", logged_in=logged_in, error3=error3, error2=error2,player=player)
    else:
        return redirect('/')


########################################################

#################### JOINED TEAM #######################

@app.get('/accept_join_request/<requestor_username>/<requestee_username>')
@login_required
def accept_join_request(requestor_username, requestee_username):
    result = model.accept_join_request(requestor_username, requestee_username)

    if result == True:
        return redirect(url_for('joined_teammates', username=requestee_username))
    else:
        abort(403)


@app.get('/joined_teammates/<username>')
@login_required
def joined_teammates(username):
    teammates = model.get_joined_teammates(username)
    logged_in = True
    return render_template('joined_team.html', teammates=teammates, logged_in=logged_in)

@app.get('/refuse_join_request/<requestor_username>/<requestee_username>')
@login_required
def refuse_join_request(requestor_username, requestee_username):
    result = model.refuse_join_request(requestor_username, requestee_username)

    if result == True:
        teammate = model.get_player_by_username(requestor_username)
        logged_in = True
        return redirect('/')
    else:
        abort(403)


if __name__=='__main__':
    app.run(port=3000,debug=True)