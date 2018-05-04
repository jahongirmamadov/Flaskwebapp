from flask import Flask,render_template,flash,redirect,url_for,session,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("No entrance","danger")
            return redirect (url_for("login"))
    return decorated_function


class RegisterForm(Form):
    name = StringField("Name:",validators = [validators.length(min=4,max=20)])
    username = StringField("Username:",validators = [validators.length(min=4, max=25)])
    email = StringField("Email Adress:", validators = [validators.email(message="Give true email adress")])
    password = PasswordField("Password:",validators = [validators.DataRequired(message="Enter password"),validators.EqualTo(fieldname="confirm",message="NO match")])
    confirm = PasswordField("Password confirmation:")

class LOginForm(Form):
    username = StringField("Username:", validators=[validators.length(min=4, max=25)])
    password = PasswordField("Password:", validators=[validators.DataRequired(message="Enter password")])

app = Flask(__name__)
app.secret_key = "ablog"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "56yn234rty"
app.config["MYSQL_DB"] = "ablog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)

@app.route("/")
def home():
    return render_template('home.html')


@app.route("/register", methods = ["POST","GET"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate() :

        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()

        sorgu = "Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()
        cursor.close()

        flash('You were successfully registered',"success")
        return redirect(url_for("login"))

    else:
        return render_template("register.html",form=form)

@app.route("/about/<string:id>")

def about(id):
    return "id is: " + id

@app.route("/control")
@login_required
def control():

    cursor = mysql.connection.cursor()

    sorgu = "Select * From articles where author = %s"
    result = cursor.execute(sorgu,(session["username"],))
    if result > 0:
        articles = cursor.fetchall()
        return render_template("control.html",articles=articles)
    else:
        return render_template("control.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/article/<string:id>")
def article(id):

    cursor=mysql.connection.cursor()

    sorgu ="Select * From articles where id = %s"
    result = cursor.execute(sorgu,(id,))
    if result > 0:
        article = cursor.fetchone()
        return render_template("article.html",article = article)
    else:
        return render_template("articles.html")



@app.route("/login",methods = ["POST", "GET"])
def login():

    form = LOginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data

        cursor = mysql.connection.cursor()
        sorgu = "Select * From users where username = %s"

        result = cursor.execute(sorgu,(username,))

        if result > 0:

            data = cursor.fetchone()
            real_password = data["password"]

            if sha256_crypt.verify(password_entered,real_password):
                session["logged_in"] = True
                session["username"] = username
                flash('You were successfully logged in',"success")
                return redirect(url_for("home"))
            else:
                flash('There is no such username or password', "danger")
                return redirect(url_for("home"))


    else:
        return render_template("login.html",form = form)


@app.route("/addarticle",methods=["GET","POST"])
@login_required
def addarticle():
    form = ArticleForm(request.form)

    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data

        cursor = mysql.connection.cursor()

        sorgu = "Insert into articles(title,author,content) VALUES(%s,%s,%s)"

        cursor.execute(sorgu,(title,session["username"],content))
        mysql.connection.commit()
        cursor.close()

        flash("Successfully added","success")
        return redirect(url_for("control"))


    return render_template("addarticle.html",form = form)


@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()

    sorgu = "Select * From articles"
    result = cursor.execute(sorgu,)
    if result > 0:
        articles = cursor.fetchall()
        return render_template("articles.html",articles= articles)
    else:
        return render_template("articles.html")

@app.route("/delete/<string:id>")
@login_required
def delete(id):

    cursor = mysql.connection.cursor()

    sorgu = "Select * From articles where author = %s and id = %s"
    result = cursor.execute(sorgu,(session["username"],id))

    if result > 0:
        sorgu2 = "Delete from articles where id = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()

        return redirect(url_for("control"))
    else:
        flash("No....","danger")
        return redirect(url_for("home"))

class ArticleForm(Form):
    title = StringField("Title",validators = [validators.length(min=4, max=25)])
    content = TextAreaField("Content",validators=[validators.length(min=4, max=250)])



if __name__ == "__main__":
    app.run(debug=True)