from flask import Flask, render_template, request,redirect,session
from werkzeug.security import generate_password_hash,check_password_hash
import mysql.connector
app = Flask(__name__)
app.secret_key = 'mysecretkey'


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2001",
    database="flask_app",
    charset="utf8",
    use_unicode=True
)

print("Connection Successful 🎉")


cursor = db.cursor()

# Home
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        #hash password
        hashed_password = generate_password_hash(password)

        #checking if user already exists
        cursor.execute("SELECT * FROM users WHERE username=%s",(username, ))
        existing_user = cursor.fetchone()

        if existing_user:
            return "User already exists ❌"

        #insert new user
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query,(username, hashed_password))
        db.commit()

        return "User registered successfully 🎉"
    return render_template('register.html')

# Login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        values = (username, password)

        cursor.execute(query,values)
        user = cursor.fetchone()

        if user:
            session['username'] = username
            return redirect('/dashboard')
        else:
            return "Invalid Credentials ❌"

    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        return render_template('dashboard.html', username=session['username'], tasks = tasks)
    else:
        return redirect('/login')

# Add Task
@app.route('/add_task', methods=['POST'])
def add_task():
    if 'username' in session:
        task = request.form['task']
        query = "INSERT INTO tasks (task) VALUES (%s)"
        cursor.execute(query,(task,))
        db.commit()

        return redirect('/dashboard')
    else:
        return redirect('/login')

# Delete Task
@app.route('/delete/<int:id>')
def delete(id):
    if 'username' in session:
        query = "DELETE FROM tasks WHERE id = %s"
        cursor.execute(query,(id,))
        db.commit()

        return redirect('/dashboard')
    else:
        return redirect('/login')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

#About
@app.route('/about')
def about():
    return render_template('about.html')

#main function
if __name__ == '__main__':
    app.run(debug = True)