from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from werkzeug.exceptions import abort
import functools

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jRv8sL2pFwXhN5aG9zQ3bU7cY6dA1eR4'

def get_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get("user_id"):
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

@app.route('/')
@login_required
def home():
    return redirect(url_for('index'))

@app.route("/index")
@login_required
def index():
    conn = get_connection()
    posts = conn.execute('SELECT posts.*, users.username AS author FROM posts JOIN users ON posts.user_id = users.id').fetchall()
    conn.close()
    return render_template("index.html", posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_connection()
        try:
            existing_user = conn.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email)).fetchone()
            if existing_user:
                flash('Username or email already exists')
                return render_template('register.html')

            conn.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                         (username, email, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('An error occurred while registering.')
            return render_template('register.html')
        finally:
            conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/admin')
@login_required
def admin():
    if session.get('username') != 'admin':
        abort(403)  # Forbidden
    conn = get_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('admin.html', users=users)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user is None or not check_password_hash(user["password"], password):
            flash("Invalid username or password")
        else:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session.get('user_id')
        if not title:
            flash("Title is required!")
        else:
            conn = get_connection()
            user_id = session['user_id']
            conn.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", (title, content, user_id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template("create.html")

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    post = get_post(id)
    if post['user_id'] != session.get('user_id') and session.get('username') != 'admin':
        abort(403)  # Forbidden
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            conn = get_connection()
            conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template("edit.html", post=post)

@app.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    if post['user_id'] != session.get('user_id') and session.get('username') != 'admin':
        abort(403)  # Forbidden
    conn = get_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash(' "{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>')
@login_required
def post(post_id):
    conn = get_connection()
    post = conn.execute('SELECT posts.*, users.username AS author FROM posts JOIN users ON posts.user_id = users.id WHERE posts.id = ?',(post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return render_template('post.html', post=post)

def get_post(post_id):
    conn = get_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
