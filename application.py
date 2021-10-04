import os
import requests
import datetime

from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from flask import redirect, render_template, request, session
from functools import wraps

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///lista.db")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/loginfp")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        mostra = request.form.get("mostra")
        data = request.form.get("data")

        if "inclui" in request.form:
            tarefa = {'tarefa' : '', 'id' : '', 'data' : data, 'tipo' : 'Cadastra'}
            return render_template("tarefa.html", tarefa=tarefa)

        if "sobe" in request.form:
            ordem = db.execute("SELECT ordem FROM tarefas WHERE id = ? ", int(request.form['sobe'][4:]))

            if ordem[0]["ordem"] > 1:
                db.execute("UPDATE tarefas SET ordem = ordem + 1 WHERE ordem = ? and data = ? and id_usuario = ?", ordem[0]["ordem"]-1, data, session["user_id"])
                db.execute("UPDATE tarefas SET ordem = ordem - 1 WHERE id = ? ", int(request.form['sobe'][4:]))

        if "desce" in request.form:
            ordem = db.execute("SELECT ordem FROM tarefas WHERE id = ? ", int(request.form['desce'][5:]))
            maior = db.execute("SELECT MAX(ordem) ordem FROM tarefas WHERE id_usuario = ? AND data = ?", session["user_id"], data)

            if ordem[0]["ordem"] != maior[0]["ordem"]:
                db.execute("UPDATE tarefas SET ordem = ordem - 1 WHERE ordem = ? and data = ? and id_usuario = ?", ordem[0]["ordem"]+1, data, session["user_id"])
                db.execute("UPDATE tarefas SET ordem = ordem + 1 WHERE id = ? ", int(request.form['desce'][5:]))

        if "feito" in request.form:
            db.execute("UPDATE tarefas set feito = 'S' WHERE id = ? ", int(request.form['feito'][5:]))

        if "desfeito" in request.form:
            db.execute("UPDATE tarefas set feito = 'N' WHERE id = ? ", int(request.form['desfeito'][8:]))

        if "altera" in request.form:
            tarefa = db.execute("SELECT tarefa, id, data, 'Altera' tipo FROM tarefas WHERE id = ?", int(request.form['altera'][6:]))
            return render_template("tarefa.html", tarefa=tarefa[0])

        if "exclui" in request.form:
            ordem = db.execute("SELECT ordem FROM tarefas WHERE id = ?", int(request.form['exclui'][6:]))

            db.execute("UPDATE tarefas SET ordem = ordem - 1 WHERE data = ? and id_usuario = ? and ordem > ?", data, session["user_id"], ordem[0]["ordem"])
            db.execute("DELETE FROM tarefas WHERE id = ? ", int(request.form['exclui'][6:]))

        if "seg" in request.form:
            date = datetime.datetime.strptime(data, "%Y-%m-%d")
            data = (date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')


        if "ant" in request.form:
            date = datetime.datetime.strptime(data, "%Y-%m-%d")
            data = (date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        if "Ocultar" in request.form:
            if request.form.get("mostra") == 'S':
                mostra = 'N'
            else:
                mostra = 'S'

        if mostra == 'N':
            todo = db.execute("SELECT id, tarefa, feito FROM tarefas WHERE id_usuario = ? and data = ? and feito = 'N' order by ordem", session["user_id"], data)
        else:
            todo = db.execute("SELECT id, tarefa, feito FROM tarefas WHERE id_usuario = ? and data = ? order by ordem", session["user_id"], data)

        return render_template("todo.html", todo=todo, data=data, mostra=mostra)

    else:
        data = f"{datetime.datetime.now():%Y-%m-%d}"
        todo = db.execute("SELECT id, tarefa, feito FROM tarefas WHERE id_usuario = ? and data = ? order by ordem", session["user_id"], data)

        return render_template("todo.html", todo=todo, data=data, mostra='S')

@app.route("/tarefa", methods=["GET", "POST"])
@login_required
def tarefa():
    if request.method == "POST":
        ordem = 1
        row = db.execute("SELECT MAX(ordem) ordem FROM tarefas WHERE id_usuario = ? AND data = ?", session["user_id"], request.form.get("data"))
        if row[0]["ordem"] != None:
            ordem = row[0]["ordem"] + 1

        if request.form['altera'][6:] != "":
            data = db.execute("SELECT data, ordem FROM tarefas WHERE id = ?", int(request.form['altera'][6:]))

            if data[0]["data"] != request.form.get("data"):
                db.execute("UPDATE tarefas SET tarefa = ?, data = ?, ordem = ? WHERE id = ? ", request.form.get("tarefa"), request.form.get("data"), ordem, int(request.form['altera'][6:]))

                db.execute("UPDATE tarefas SET ordem = ordem - 1 WHERE data = ? and id_usuario = ? and ordem > ?", data[0]["data"], session["user_id"], data[0]["ordem"])
            else:
                db.execute("UPDATE tarefas SET tarefa = ?, data = ? WHERE id = ? ", request.form.get("tarefa"), request.form.get("data"), int(request.form['altera'][6:]))

        else:
            db.execute("INSERT INTO tarefas (tarefa, data, id_usuario, ordem) VALUES(?, ?, ?, ?)",
                       request.form.get("tarefa"), request.form.get("data"), session["user_id"], ordem)

        todo = db.execute("SELECT id, tarefa, feito FROM tarefas WHERE id_usuario = ? and data = ? order by ordem", session["user_id"], request.form.get("data"))

        return render_template("todo.html", todo=todo, data=request.form.get("data"), mostra='S')

    else:
        return render_template("tarefa.html")


@app.route("/loginfp", methods=["GET", "POST"])
def loginfp():
    session.clear()

    if request.method == "POST":
        rows = db.execute("SELECT * FROM usuario WHERE usuario = ?", request.form.get("usuario"))
        erro = ''

        if len(rows) != 1 or not check_password_hash(rows[0]["senha"], request.form.get("senha")):
            erro = 'Verifique o login e a senha para continuar.'
            return render_template("loginfp.html", erro=erro)

        session["user_id"] = rows[0]["id"]

        return redirect("/")
    else:
        return render_template("loginfp.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        retorna_erro = 'N'
        erro = ''

        if request.form.get("senha") != request.form.get("confirmacao"):
            erro = 'Senhas diferentes.'
            retorna_erro = 'S'

        rows = db.execute("SELECT * FROM usuario WHERE usuario = ?", request.form.get("usuario"))

        if len(rows) == 1:
            erro = 'login'
            retorna_erro = 'S'

        if retorna_erro == 'S':
            return render_template("cadastro.html", erro=erro)

        nome = request.form.get("nome")
        usuario = request.form.get("usuario")
        senha = generate_password_hash(request.form.get("senha"))

        id_usuario = db.execute("INSERT INTO usuario (nome, usuario, senha) VALUES(?, ?, ?)", nome, usuario, senha)

        session["user_id"] = id_usuario

        return redirect("/")
    else:
        return render_template("cadastro.html")

@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")
