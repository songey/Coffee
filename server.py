from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
from db import connectToMySQL
app = Flask(__name__)
app.secret_key = "Lord of the Rings"
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
########################################################################################

@app.route("/")
def root():

    if 'userid' not in session:
        return render_template("index.html")

    id = session['userid']
    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM readers WHERE id="+str(id)+";"
    user = mysql.query_db(query)

    return render_template("index.html", user=user)

########################################################################################
@app.route("/createAccount")
def goToRegister():

    if 'userid' not in session:
        return render_template("register.html")    
    return redirect("/")

########################################################################################
@app.route("/login", methods=['POST'])
def login():

    mysql = connectToMySQL('books_coffee')
    query = "SELECT * FROM readers WHERE username = %(username)s;"
    data = { 'username': request.form['username'] }
    result = mysql.query_db(query, data)

    if result:
        if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
            session['userid'] = str(result[0]['id'])
            return redirect("/")

    flash("Failure to login", "login")
    return redirect("/")

########################################################################################
@app.route("/register", methods=['POST'])
def register():

    is_valid = True

    if len(request.form['username']) < 1:
        is_valid = False
        flash("Please enter a username", "username")

    if len(request.form['username']) > 1 and len(request.form['username']) < 4:
        is_valid = False
        flash("Username: at least 4 characters", "username")

    if len(str(request.form['username'])) > 15:
        is_valid = False
        flash("Username max: 15 characters", "length")

    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM readers WHERE username = %(username)s"
    data = { 'username': request.form['username'] }
    result = mysql.query_db(query, data)

    if result:
        is_valid = False
        flash("This username already exists...", "username")

    if len(request.form['password']) < 1:  
        is_valid = False
        flash("Please enter a password", "password")

    if len(request.form['password']) > 0 and len(request.form['password']) < 4:
        is_valid = False
        flash("...", "password")

    if is_valid == False:
        return redirect("/createAccount")
    
    password_hash = bcrypt.generate_password_hash(request.form['password'])
    mysql = connectToMySQL('books_coffee')
    query = "INSERT INTO readers (username, password, updated_at, created_at) VALUES (%(username)s, %(password_hash)s, NOW(), NOW())"
    data = {
        'username': request.form['username'],
        'password_hash': password_hash
    }
    id = mysql.query_db(query, data)
    session['userid'] = str(id)

    return redirect("/")

########################################################################################
@app.route("/bookClub")
def bookClub():

    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM readers;"
    readers = mysql.query_db(query)

    return render_template("bookClub.html", readers=readers)

########################################################################################
@app.route("/homePage")
def homePage():

    if 'userid' not in session:
        return redirect("/")

    id = session['userid']
    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM readers WHERE id="+str(id)+";"
    reader = mysql.query_db(query)

    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM books WHERE books.reader_id ="+session['userid']+";"
    books = mysql.query_db(query)

    return render_template("homePage.html", reader=reader, books=books)

########################################################################################
@app.route("/edit/<id>")
def editPage(id):
   
    if 'userid' not in session:
        return redirect("/")
    
    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM readers WHERE id="+session['userid']
    user = mysql.query_db(query)

    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM books WHERE id="+str(id)+";"
    book = mysql.query_db(query)

    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM posts WHERE book_id="+str(id)+";"
    posts = mysql.query_db(query)

    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM comments"
    comments = mysql.query_db(query)

    return render_template("edit.html", user=user, book=book, posts=posts, comments=comments)

########################################################################################
@app.route("/editBook", methods=['POST'])
def editBook():
   
    id = request.form['id']

    if len(request.form['title']) < 1:
        flash("Please enter a title", "title")
        return redirect("/edit/"+str(id))

    mysql = connectToMySQL("books_coffee")
    query = "UPDATE books SET title = %(title)s, author = %(author)s, pages = %(pages)s, status = %(status)s WHERE id = %(id)s"
    data = {
        "title": request.form['title'],
        "author": request.form['author'],
        "pages": request.form['pages'],
        "status": request.form['status'],
        "id" : request.form["id"]
    }
    mysql.query_db(query, data)
    
    return redirect("/homePage")

########################################################################################
@app.route("/addPost", methods=['POST'])
def post():

    id = request.form['id']

    if len(request.form['content']) < 2:
        flash("Please enter a post", "post")
        return redirect("/edit/"+str(id))

    mysql = connectToMySQL("books_coffee")
    query = "INSERT INTO posts (content, book_id, reader_id, updated_at, created_at) VALUES (%(content)s, %(book_id)s, %(reader_id)s, NOW(), NOW())"
    data = {
        'content': request.form['content'],
        'book_id': request.form["id"],
        'reader_id': session['userid']
    }
    mysql.query_db(query, data)

    return redirect("/homePage")

########################################################################################
@app.route("/readerPage/<id>")
def home(id):

    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM books WHERE books.reader_id ="+str(id)+";"
    books = mysql.query_db(query)

    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM readers WHERE id="+str(id)+";"
    reader = mysql.query_db(query)

    return render_template("readerPage.html", reader=reader, books=books)

########################################################################################
@app.route("/readerBook/<id>")
def bookReview(id):

    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM books WHERE id="+str(id)+";"
    book = mysql.query_db(query)

    mysql = connectToMySQL("books_coffee")
    query = "SELECT readers.username FROM books JOIN readers ON books.reader_id = readers.id WHERE books.id="+str(id)+";"
    poster = mysql.query_db(query)

    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM posts WHERE book_id="+str(id)+";"
    posts = mysql.query_db(query)

    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM books_coffee.comments JOIN posts ON comments.post_id = posts.id WHERE posts.book_id ="+str(id)+";"
    comments = mysql.query_db(query)

    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM readers;"
    readers = mysql.query_db(query)

    if 'userid' not in session:
        return render_template("readerBook.html", book=book, posts=posts, comments=comments, poster=poster, readers=readers)
    
    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM readers WHERE id="+session['userid']
    user = mysql.query_db(query)

    return render_template("readerBook.html", user=user, book=book, posts=posts, comments=comments, poster=poster, readers=readers)

########################################################################################
@app.route("/leaveComment", methods=['POST'])
def leaveComment():

    id = request.form['book_id']

    if len(request.form['content']) < 2:
        return redirect("/readerBook/"+str(id))

    mysql = connectToMySQL("books_coffee")
    query = "INSERT INTO comments (content, post_id, reader_id, updated_at, created_at) VALUES (%(content)s, %(post_id)s, %(reader_id)s, NOW(), NOW())"
    data = {
        'content': request.form['content'],
        'post_id': request.form['id'],
        'reader_id': session['userid']
    }
    mysql.query_db(query, data)
    print(query)

    return redirect("/readerBook/"+str(id))

########################################################################################
@app.route("/addBook", methods=['POST'])
def addBook():

    is_valid = True

    if len(request.form['title']) < 1:
        is_valid = False
        flash("Please enter a title:", "title")

    if is_valid == False:
        return redirect("/homePage")

    mysql = connectToMySQL("books_coffee")
    query = "INSERT INTO books (title, author, pages, status, reader_id, updated_at, created_at) VALUES (%(title)s, %(author)s, %(pages)s, %(status)s, %(id)s, NOW(), NOW())"
    data = {
        'title': request.form['title'],
        'author': request.form['author'],
        'pages': request.form['pages'],
        'status': request.form['status'],
        'id': session['userid']
    }
    mysql.query_db(query, data)

    return redirect("/homePage")

########################################################################################
@app.route("/removeBook", methods=['POST'])
def removeBook():

    mysql = connectToMySQL("books_coffee")
    query = "UPDATE books SET status = %(status)s WHERE id = %(id)s"
    data = {
        "status": "removed",
        "id": request.form['id']
    }
    mysql.query_db(query, data)
    
    return redirect("/homePage")

########################################################################################
@app.route("/addSpoilPost", methods=['POST'])
def addSpoilPost():

    if len(request.form['title']) < 1:
        flash("Please enter title / post", "post")
        return redirect("/addSpoil")
    if len(request.form['content']) < 1:
        flash("Please enter title / post", "post")
        return redirect("/addSpoil")

    mysql = connectToMySQL("books_coffee")
    query = "INSERT INTO spoils (reader_id, title, status, content, updated_at, created_at) VALUES (%(id)s, %(title)s, %(status)s, %(content)s, NOW(), NOW())"
    data = {
        'id': session['userid'],
        'title': request.form['title'],
        'status': request.form['status'],
        'content': request.form['content']
    }
    mysql.query_db(query, data)

    return redirect("/spoilerRoom")

########################################################################################
@app.route("/spoilerRoom")
def spoilerRoom():

    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM spoils;"
    spoils = mysql.query_db(query)

    if 'userid' not in session:
        print("No user in session")
    else:
        id = session['userid']
        mysql = connectToMySQL("books_coffee")
        query = "SELECT * FROM readers WHERE id="+str(id)+";"
        user = mysql.query_db(query)
        return render_template("spoilerRoom.html", user=user, spoils=spoils)

    return render_template("spoilerRoom.html", spoils=spoils)

########################################################################################
@app.route("/addSpoil")
def addSpoil():

    if 'userid' not in session:
        return render_template("spoilerRoom.html")
    
    id = session['userid']
    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM readers WHERE id="+str(id)+";"
    user = mysql.query_db(query)

    return render_template("addSpoil.html", user=user)

########################################################################################
@app.route("/spoilerBook/<id>")
def book(id):

    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM spoils WHERE id="+str(id)+";"
    spoil = mysql.query_db(query)

    mysql = connectToMySQL("books_coffee")
    query = "SELECT readers.username FROM readers JOIN spoils ON spoils.reader_id = readers.id WHERE spoils.id="+str(id)+";"
    spoiler = mysql.query_db(query)

    mysql = connectToMySQL("books_coffee")
    query = "SELECT readers.username, spoil_comments.comment FROM spoil_comments JOIN readers ON spoil_comments.reader_id = readers.id WHERE spoil_id="+str(id)+";"
    comments = mysql.query_db(query)

    if 'userid' not in session:
        return render_template("spoilerBook.html", spoil=spoil, comments=comments, spoiler=spoiler)

    id = session['userid']
    mysql = connectToMySQL("books_coffee")
    query = "SELECT * FROM readers WHERE id="+str(id)+";"
    user = mysql.query_db(query)

    return render_template("spoilerBook.html", user=user, spoil=spoil, comments=comments, spoiler=spoiler)

########################################################################################
@app.route("/spoilComment", methods=['POST'])
def spoilComment():

    id = request.form['id']
    
    if len(request.form['comment']) < 2:
        return redirect("/spoilerBook/"+str(id))

    mysql = connectToMySQL("books_coffee")
    query = "INSERT INTO spoil_comments (spoil_id, reader_id, comment, updated_at, created_at) VALUES (%(spoil_id)s, %(reader_id)s, %(comment)s, NOW(), NOW())"
    data = {
        'spoil_id': request.form['id'],
        'reader_id': session['userid'],
        'comment': request.form['comment']
    }
    mysql.query_db(query, data)

    return redirect("/spoilerBook/"+str(id))

########################################################################################
@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")

########################################################################################
if __name__=='__main__':
    app.run(debug=True)