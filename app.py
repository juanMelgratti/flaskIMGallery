from flask import Flask, render_template, request, session, escape, redirect, url_for, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import random
import os

UPLOAD_FOLDER = os.path.abspath('./static/img')
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpge"])

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///post.db' 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
app.secret_key = 'dev'

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(25), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(30), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    img = db.Column(db.Text, nullable=False)

class Users(db.Model):
    author_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(25), nullable=False)
    secret_key = db.Column(db.String(10), nullable=False)

@app.route("/")
@app.route("/home")
def home():
    if "username" in session:
        return redirect('/posts')
    return render_template('home.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["username"] = user.username
            return redirect('/posts')
            
        return redirect('/signup')
    elif "username" in session:
        return redirect('/posts')
    return render_template("login.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def recover_password():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form["username"]).first()
        if user.secret_key == request.form['secret_key']:
            if request.form["password"] != "" and (request.form["password"] == request.form["confirm"]) and not " " in request.form["password"]:
                hashed_pw = generate_password_hash(request.form["password"], method="sha256")
                user.password = hashed_pw 
                db.session.commit()
                return "password changed"
    return render_template('recover.html')

@app.route("/signup", methods=["GET", "POST"])
def signup():    
    if not "username" in session:
        if request.method == "POST":
            if request.form["password"] != "" and (request.form["password"] == request.form["confirm"]) and request.form["secret_word"] != "" and len(request.form["password"])<25 and request.form["username"] != "" and not " " in request.form["username"]:
                if not " " in request.form["password"] and (not " " in request.form["secret_word"]) and len(request.form["secret_word"])<10: 
                    hashed_pw = generate_password_hash(request.form["password"], method="sha256")
                    new_user = Users(username=request.form["username"], password=hashed_pw, secret_key=request.form["secret_word"])
                    exist_username = db.session.query(Users.username).filter_by(username=request.form['username']).scalar() is not None
                    if not exist_username and len(request.form["username"])< 30:
                        db.session.add(new_user)
                        db.session.commit()
                        return redirect('/login')
                    else:
                        return render_template('signuperror.html')
                else:
                    return render_template("signuperror2.html")
            else:
                return render_template("signuperror2.html")
        return render_template("signup.html")
    else:
        return redirect("/posts")

@app.route("/logout")
def logout():
        session.pop("username", None)
        return redirect("/login")

@app.route("/posts", methods=["GET", "POST"])
def post():
    n = random.random()
    if "username" in session:
        user = session["username"]
        if request.method == "POST":
            if not "file" in request.files:
                return "No file part in the form."
            f = request.files["file"]
            if f.filename == "":
                return "No file selected."
            if f and allowed_file(f.filename) and len(request.form["title"])<25 and len(request.form["content"])<300:
                filename = user + str(n) + secure_filename(f.filename)
                f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                post_title = request.form["title"]
                post_content = request.form["content"] 
                new_post = BlogPost(title=post_title, content=post_content, author=user, img=filename)
                db.session.add(new_post)
                db.session.commit()
            return redirect('/posts')       
        else:
            all_posts = BlogPost.query.filter_by(author=user)
            return render_template("post.html", posts=all_posts)
    return "you must login first"

@app.route('/posts/delete/<int:id>')
def delete(id):
    post = BlogPost.query.get_or_404(id)
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.img))
    db.session.delete(post)
    db.session.commit()
    return redirect('/posts')

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    post = BlogPost.query.get_or_404(id)
    user = session["username"]
    if "username" in session and user == post.author:
        if request.method == 'POST'and len(request.form["title"])<25:
            post.title = request.form['title']
            post.content = request.form['content']
            db.session.commit()
            return redirect('/posts')
        else: 
            post = BlogPost.query.get_or_404(id)   
            return render_template('edit.html', post=post)
    else:
        return redirect('/home')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if "username" in session:
        if request.method == 'POST':
            post = request.form["search"]
            user_posts = BlogPost.query.filter_by(author=post) 
            title_posts = BlogPost.query.filter_by(title=post)
            return render_template('search.html', posts=user_posts, title=title_posts)
        return render_template('search.html')
    else:
        if request.method == 'POST':
            post = request.form["search"]
            user_posts = BlogPost.query.filter_by(author=post) 
            title_posts = BlogPost.query.filter_by(title=post)
            return render_template('search.html', posts=user_posts, title=title_posts)
        return render_template('search2.html')

@app.route('/posts/image/<int:id>', methods=['GET', 'POST'])
def image(id):
    img = BlogPost.query.get_or_404(id)
    return render_template('image.html', img=img)



















if __name__ =="__main__":
    db.create_all()
    app.run(debug=True)

