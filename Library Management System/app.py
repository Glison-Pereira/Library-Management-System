from flask import *
from sqlite3 import *
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

@app.route('/', methods=["GET", "POST"])
def library():
    con = None
    try:
        con = connect("library.db")
        cursor = con.cursor()
        if request.method=="POST":
            search=request.form['search']
            sql = "SELECT * FROM user where book like ?"
            cursor.execute(sql,('%' + search + '%',))
            data = cursor.fetchall()
            return render_template("library.html", msg=data)
        else:
            sql = "SELECT * FROM user"
            cursor.execute(sql)
            data = cursor.fetchall()
            return render_template("library.html", msg=data)
    except Exception as e:
        msg = "Issue: " + str(e)
        return render_template("library.html", msg=msg)
    finally:
        if con is not None:
            con.close()

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form['name']
        password = request.form['password']
        con = None
        try:
            con = connect("library.db")
            cursor = con.cursor()
            sql = "INSERT INTO login (name, password) VALUES (?, ?)"
            cursor.execute(sql, (name, password))
            con.commit()
            session['name'] = name
            return redirect(url_for("user"))
        except Exception as e:
            con.rollback()
            msg = "Issue: " + str(e)
            return render_template('login.html', msg=msg)
        finally:
            if con is not None:
                con.close()
    else:
        return render_template('login.html')

@app.route('/user', methods=["GET", "POST"])
def user():
    if 'name' not in session:
        return redirect(url_for('login'))
    name = session['name']
    con = None
    data = []
    msg = ""
    if request.method == "POST":
        book = request.form['book']
        author = request.form['author']
        page = request.form['page']
        link = request.form['link']
        try:
            con = connect("library.db")
            cursor = con.cursor()
            if 'Submit' in request.form:
                sql = "INSERT INTO user (book, author, description, link, name) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(sql, (book, author, page, link, name))
                con.commit()
                msg = "Book added successfully!"
            elif 'Delete' in request.form:
                sql = "DELETE FROM user WHERE book = ? AND name = ?"
                cursor.execute(sql, (book, name))
                con.commit()
                msg = "Book deleted successfully!"
            elif 'Update' in request.form:
                sql = "UPDATE user SET author = ?, description = ?, link = ? WHERE book = ? AND name = ?"
                cursor.execute(sql, (author, page, link, book, name))
                con.commit()
                msg = "Book updated successfully!"
            sql = "SELECT * FROM user WHERE name = ?"
            cursor.execute(sql, (name,))
            data = cursor.fetchall()
        except Exception as e:
            con.rollback()
            msg = "Issue: " + str(e)
        finally:
            if con is not None:
                con.close()
    return render_template("user.html", data=data, msg=msg)

if __name__ == "__main__":
    app.run(debug=True)
