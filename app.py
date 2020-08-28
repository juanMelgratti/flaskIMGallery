from flask import Flask, render_template, request, session, escape, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash 

import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///post.db' 
db = SQLAlchemy(app)
app.secret_key = 'dev'

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False, default="N/A")
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return "post created " + str(self.id)

class Image(db.Model):
    img_id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer)
    image = db.Column(db.LargeBinary, nullable=False)

class Users(db.Model):
    author_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(80), nullable=False)


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["username"] = user.username
            return redirect('/posts')
            
        return redirect('/signup')

    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        hashed_pw = generate_password_hash(request.form["password"], method="sha256")
        new_user = Users(username=request.form["username"], password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template("signup.html")

@app.route("/logout")
def logout():
        session.pop("username", None)
        return redirect("/login")

@app.route("/posts", methods=["GET", "POST"])
def post():
    if "username" in session:
        if request.method == "POST":
            post_title = request.form["title"]
            post_content = request.form["content"]
            user = session["username"]
            new_post = BlogPost(title=post_title, content=post_content, author=user)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/posts')
            
        else:
            user = session["username"]
            all_posts = BlogPost.query.filter_by(author=user)
            return render_template("post.html", posts=all_posts)
            #no lo renderiza mágicamente. Los post abajo están en orden de posteo hecho por un for
    return "you must login first"

@app.route('/posts/delete/<int:id>')
def delete(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/posts')

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        post = BlogPost.query.get_or_404(id)
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect('/posts')
    else: 
        post = BlogPost.query.get_or_404(id)   
        return render_template('edit.html', post=post)

@app.route('/upload_img', methods=['GET', 'POST'])
def upload():
    pass



















if __name__ =="__main__":
    db.create_all()
    app.run(debug=True)

