import base64, sqlite3

from flask import Flask, render_template, redirect, request, jsonify, json
from flask_login import LoginManager, login_required, current_user, login_user, logout_user, login_manager
from flask_bcrypt import Bcrypt

from database import Database
from helpers import query_into_dict, word_count, apology, upload_image, is_allowed_file, validate_file_size
from models import User, Post

# Initilize app
app = Flask(__name__)

app.secret_key = "$uP3rS3cr3tK3yF0rFl@sk!2024"
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png']

# Initilize database
db = Database("database.db")
db.init_db()

# Initilize bcrypt
bcrypt = Bcrypt(app)

# Initilize login manager
login_manager = LoginManager(app)

# Route logic
@login_manager.user_loader
def load_user(user_id): 
    return User(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect("/login")

@app.route('/')
@login_required
def index():
    post_id_list = [d['id'] for d in query_into_dict("SELECT posts.id FROM posts ORDER BY posts.created_at DESC LIMIT 5")]
    posts = []
    for row in post_id_list:
        post = Post(row, current_user.id)
        posts.append(post)
    
    return render_template('home/index.html', posts=posts, is_allow_creating=True)


@app.route('/marked')
@login_required
def marked():
    post_id_list = [d['id'] for d in query_into_dict('''
        SELECT 
            marks.post_id AS id
        FROM 
            marks 
        JOIN
            users ON marks.user_id = users.id
        WHERE
            users.id = ?
        ORDER BY 
            marks.marked_at DESC
    ''', (current_user.id,))]

    posts = []

    for row in post_id_list:
        post = Post(row, current_user.id)
        posts.append(post)

    return render_template('home/index.html', posts=posts, is_allow_creating=False)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")
    elif request.method == "POST":
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Username validation
        if not firstName:
            return jsonify({"error": "Missing first name!"})
        elif not firstName.isalpha():
            return jsonify({"error": "First name must be alphabetic and contains no space!"})
        elif not lastName:
            return jsonify({"error": "Missing last name!"})
        elif not lastName.isalpha():
            return jsonify({"error": "Last name must be alphabetic and contains no space!"})
        elif not username:
            return jsonify({"error": "Missing username!"})
        elif len(query_into_dict("SELECT * FROM users WHERE username = ?", (username,))) > 0:
            return jsonify({"error": "Username already existed!"})
        elif not username.isidentifier():
            return jsonify({"error": "Username must not include special characters (including 'space') or start with a number!"})
        elif len(username) < 8 or len(username) > 16:
            return jsonify({"error": "Username length must be between 8 and 16 characters!"})
        
        # Password validation
        elif not password:
            return jsonify({"error": "Missing passwords!"})
        elif len(password) <= 8:
            return jsonify({"error": "Password length must be longer than 8 characters!"})
        elif not any(char.isdigit() for char in password):
            return jsonify({"error": "Password must have at least one number!"})
        elif not any(char.isupper() for char in password):
            return jsonify({"error": "Password must have at least one uppercase letter!"})
        elif not any(char.islower() for char in password):
            return jsonify({"error": "Password must have at least one lowercase letter!"})
        elif not any(char in ['$', '@', '#', '%'] for char in password):
            return jsonify({"error": "Password must have at least one of the symbols $, @, #, %"})
        elif not confirmation:
            return jsonify({"error": "Missing confirmation!"})
        elif password != confirmation:
            return jsonify({"error": "Password do not match!"})
        else:
        # Insert new user into database
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            defaultBio = 'Hello world, my name is ' + firstName
            db.cursor.execute("INSERT INTO users (username, password, first_name, last_name, bio) VALUES (?,?,?,?,?)", (username, hashed_password, firstName, lastName, defaultBio))
            db.conn.commit()
            return jsonify({"message": "Registration Successful!"})
        
    
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        isRemember = request.form.get("isRemember")

        if not username:
            return jsonify({"error": "Missing username!"})
        elif not password:
            return jsonify({"error": "Missing password!"})
        else:
            userData = query_into_dict("SELECT * FROM users WHERE username = ?", (username,))

            if len(userData) == 0  or not bcrypt.check_password_hash(userData[0]["password"], password):
                return jsonify({"error": "Invalid username or password!"})
            
            user = User(userData[0]["id"])
            login_user(user, remember=isRemember)

            return jsonify({"message": "Logged In!"})
        
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect("/login")

    
@app.route('/profile/<username>')
@login_required
def profile(username):

    userData = query_into_dict("SELECT * FROM users WHERE username = ?", (username,))

    if len(userData) > 0:
        user = User(userData[0]["id"])
        post_id_list = [d['id'] for d in query_into_dict("SELECT posts.id FROM posts JOIN users ON posts.user_id = users.id WHERE users.id = ? ORDER BY posts.created_at DESC", (user.id,))]

        posts = []
        for row in post_id_list:
            post = Post(row, current_user.id)
            posts.append(post)

        return render_template("user_profile/profile.html", user=user, posts=posts)
    else: 
        return apology("User's not found", 404)

    
@app.route('/edit/profile', methods=["POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        profilePicture = request.files.get("profilePicture")
        wallpaperPicture = request.files.get("wallpaperPicture")
        username = request.form.get("username")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        bio = request.form.get("bio")
        
        if profilePicture:
            if not is_allowed_file(profilePicture):
                return jsonify({"error": "Invalid file name or file type!"})
            if not validate_file_size(profilePicture):
                return jsonify({"error": "Image files must be smaller than 7 MB!"})
            
        if wallpaperPicture:
            if not is_allowed_file(wallpaperPicture):
                return jsonify({"error": "Invalid file name or file type!"})
            if not validate_file_size(wallpaperPicture):
                return jsonify({"error": "Image files must be smaller than 7 MB!"})

        if not username:
            return jsonify({"error": "Missing username!"})
        elif not firstname:
            return jsonify({"error": "Missing first name!"})
        elif not lastname:
            return jsonify({"error": "Missing last name!"})
        elif not username.isidentifier():
            return jsonify({"error": "Invalid username!"})
        elif username != current_user.username and len(query_into_dict("SELECT * FROM users WHERE username = ?", (username,))) > 0:
            return jsonify({"error": "This username already exists!"})
        elif len(username) < 8 or len(username) > 16:
            return jsonify({"error": "Username length must be between 8 and 16 characters!"})
        elif not firstname.isalpha() or not lastname.isalpha():
            return jsonify({"error": "First name and last name must be alphabetic and contains no space!"})
        elif word_count(bio) > 200:
            return jsonify({"error": "Your bio must not exceed 200 words!"})
        else:
            # Updating new information
            if profilePicture:
                upload_image(profilePicture, 'profile_picture')
            if wallpaperPicture:
                upload_image(wallpaperPicture, 'wallpaper_picture')
            
            if current_user.username != username or current_user.first_name != firstname or current_user.last_name != lastname or current_user.bio != bio:
                db.cursor.execute("UPDATE users SET username = ?, first_name = ?, last_name = ?, bio = ? WHERE id = ?", (username, firstname, lastname, bio, current_user.id))
                db.conn.commit()
            
            return jsonify({"message": "Save changes!"})


@app.route("/search")
@login_required
def search():
    query = request.args.get("q")
    
    if query:
        condition = "first_name LIKE '%" + query + "%'" + " OR " + "last_name LIKE '%" + query + "%'"  + " OR " + "username LIKE '%" + query + "%'"
        search_results = query_into_dict("SELECT * FROM users WHERE " + condition + " ORDER BY first_name")

        print

        # Parse the BLOB into JSON 
        for result in search_results:
            if result['profile_picture'] is not None:
                result['profile_picture'] = base64.b64encode(result['profile_picture']).decode('utf-8')
            if result['wallpaper_picture'] is not None:
                result['wallpaper_picture'] = base64.b64encode(result['wallpaper_picture']).decode('utf-8')

        current_user.search = query
        return render_template("home/index.html", user=current_user, query=query, search_results=search_results)
    else:
        return redirect("/")


@app.route("/posting", methods=["POST"])
@login_required
def posting():
    if request.method == "POST":
        caption = request.form.get("caption")
        files = request.files.getlist("image")

        image_list = []
            
        if not caption and not files:
            return jsonify({"error": "You can submit an empty post!"})
        elif len(caption) > 2500:
            return jsonify({"error": "You can only write a caption which is shorter than 2500 characters!"})
        elif len(files) > 10:
            return jsonify({"error": "You can only upload 10 or less pictures!"})
        elif not is_allowed_file(files, True):
            return jsonify({"error": "Invalid file name or file type!"})
        elif not validate_file_size(files, True):
            return jsonify({"error": "Image files must be smaller than 7 MB!"})
        
        
        db.cursor.execute("INSERT INTO posts (user_id, caption, media_count) VALUES (?,?,?)", (current_user.id, caption, len(files)))
        
        for file in files:
            file_data = file.read()
            file_tuple = (db.cursor.lastrowid, "image", sqlite3.Binary(file_data))
            image_list.append(file_tuple)

        db.cursor.executemany("INSERT INTO post_media (post_id, media_type, media_blob) VALUES (?,?,?)", image_list)
        db.conn.commit()
        
        return jsonify({"message": "Successful!"})

@app.route("/post/like", methods=["POST"])
@login_required
def like_post():
    id = request.form.get('id')
    
    current_like = query_into_dict("SELECT * FROM likes WHERE post_id = ? AND user_id = ?", (id, current_user.id))

    if len(current_like) == 0:
        db.cursor.execute("INSERT INTO likes (post_id, user_id) VALUES (?,?)", (id, current_user.id))
    else:
        db.cursor.execute("DELETE FROM likes WHERE post_id = ? AND user_id = ?", (id, current_user.id))
    db.conn.commit()

    likes = query_into_dict('''
        SELECT 
            *
        FROM 
            likes 
        JOIN 
            posts ON likes.post_id = posts.id 
        WHERE 
            posts.id = ?
    ''', (id,))
    
    return jsonify({'message': 'Liked Successful!', 'like_count' : len(likes)})

@app.route("/post/comment", methods=["POST"])
@login_required
def comment_post():
    id = request.form.get('id')
    comment = request.form.get('comment')

    if len(comment) == 0:
        return jsonify({"error": 'Comment must not be empty'})
    elif len(comment) > 2000:
        return jsonify({"error": "Comment must not exceed 2000 characters!"})
    
    db.cursor.execute("INSERT INTO comments (post_id, user_id, content) VALUES (?,?,?)", (id, current_user.id, comment))
    db.conn.commit()

    comments = query_into_dict('''
        SELECT 
            *
        FROM 
            comments 
        JOIN 
            posts ON comments.post_id = posts.id 
        WHERE 
            posts.id = ?
    ''', (id,))
    
    return jsonify({
        'message': 'Commented Successful!', 
        'cmt_count': len(comments), 
        'username': current_user.username,
        'display_name': current_user.first_name + ' ' + current_user.last_name,
        'profile_picture': current_user.profile_picture,
    })

@app.route("/post/delete", methods=["POST"])
@login_required
def delete_post():
    id = request.form.get('id')

    db.cursor.execute("DELETE FROM posts WHERE id = ?",(id,))
    db.cursor.execute("DELETE FROM post_media WHERE post_id = ?",(id,))
    db.cursor.execute("DELETE FROM marks WHERE post_id = ?",(id,))
    db.cursor.execute("DELETE FROM likes WHERE post_id = ?",(id,))
    db.cursor.execute("DELETE FROM comments WHERE post_id = ?",(id,))
    db.conn.commit()

    return jsonify({'message': 'Post Deleted Successful!'})


@app.route("/post/mark", methods=["POST"])
@login_required
def mark_post():
    id = request.form.get('id')
    
    current_mark = query_into_dict("SELECT * FROM marks WHERE post_id = ?", (id,))

    if len(current_mark) == 0:
        db.cursor.execute("INSERT INTO marks (post_id, user_id) VALUES (?,?)", (id, current_user.id))
    else:
        db.cursor.execute("DELETE FROM marks WHERE post_id = ? AND user_id = ?", (id, current_user.id))
    db.conn.commit()

    return jsonify({'message': 'Marked Successful!'})

if __name__ == '__main__':
    app.run(debug=True)