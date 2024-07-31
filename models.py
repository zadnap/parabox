from flask_login import UserMixin, current_user
import base64
from helpers import query_into_dict, format_created_at

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id
        user = query_into_dict("SELECT * FROM users WHERE id = ?", (user_id,))[0]
        self.username = user["username"]
        self.first_name = user["first_name"]
        self.last_name = user["last_name"]
        self.password_hashed = user["password"]
        self.bio = user["bio"]
        self.profile_picture = base64.b64encode(user["profile_picture"]).decode("utf-8") if user["profile_picture"] else None
        self.wallpaper_picture = base64.b64encode(user["wallpaper_picture"]).decode("utf-8") if user["wallpaper_picture"] else None
        self.search = ''

class Post():
    def __init__(self, post_id, current_user_id):
        post = query_into_dict('''
            SELECT 
                posts.id,
                users.username,
                users.first_name,
                users.last_name,
                users.profile_picture,
                posts.caption,
                posts.media_count,
                julianday('now') - julianday(posts.created_at) AS created_at_day,
                strftime('%s', 'now') - strftime('%s', posts.created_at) AS created_at_second,
                post_media.media_blob
            FROM 
                posts 
            LEFT JOIN 
                users ON posts.user_id = users.id
            LEFT JOIN 
                post_media ON posts.id = post_media.post_id
            WHERE 
                posts.id = ?
        ''', (post_id,))
        likes = query_into_dict('''
            SELECT 
                users.username,
                users.first_name,
                users.last_name,
                users.profile_picture
            FROM 
                likes 
            JOIN 
                posts ON likes.post_id = posts.id 
            JOIN
                users ON likes.user_id = users.id
            WHERE 
                posts.id = ?
        ''', (post_id,))
        is_liked = query_into_dict('''
            SELECT 
                *
            FROM 
                likes
            JOIN
                posts ON likes.post_id = posts.id 
            JOIN
                users ON likes.user_id = users.id
            WHERE 
                posts.id = ? AND users.id = ?
        ''', (post_id, current_user_id))
        is_marked = query_into_dict('''
            SELECT 
                *
            FROM 
                marks
            JOIN
                posts ON marks.post_id = posts.id 
            JOIN
                users ON marks.user_id = users.id
            WHERE 
                posts.id = ? AND users.id = ?
        ''', (post_id, current_user_id))
        comments = query_into_dict('''
            SELECT 
                users.username,
                users.first_name,
                users.last_name,
                users.profile_picture,
                comments.content,
                comments.created_at,
                julianday('now') - julianday(comments.created_at) AS created_at_day,
                strftime('%s', 'now') - strftime('%s', comments.created_at) AS created_at_second
            FROM 
                comments 
            JOIN 
                posts ON comments.post_id = posts.id
            JOIN 
                users ON comments.user_id = users.id 
            WHERE 
                posts.id = ?
            ORDER BY comments.created_at
        ''', (post_id,))

        for comment in comments:
            comment["profile_picture"] = base64.b64encode(comment["profile_picture"]).decode('utf-8') if comment["profile_picture"] else None
            comment['created_at'] = format_created_at(comment['created_at_day'], comment['created_at_second'])

        self.id = post[0]["id"]
        self.username = post[0]["username"]
        self.first_name = post[0]["first_name"]
        self.last_name = post[0]["last_name"]
        self.profile_picture = base64.b64encode(post[0]["profile_picture"]).decode('utf-8') if post[0]["profile_picture"] else None
        self.caption = post[0]["caption"]
        self.media_count = post[0]["media_count"]
        self.likes = likes
        self.is_liked = False if len(is_liked) == 0 else True
        self.is_marked = False if len(is_marked) == 0 else True
        self.comments = comments
        self.created_at = format_created_at(post[0]['created_at_day'], post[0]['created_at_second'])
        self.media_blobs = [base64.b64encode(row["media_blob"]).decode('utf-8') for row in post if row["media_blob"]]
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_picture': self.profile_picture,
            'caption': self.caption,
            'media_count': self.media_count,
            'likes': self.likes,
            'is_liked': self.is_liked,
            'is_marked': self.is_marked,
            'comments': self.comments,
            'created_at': self.created_at,
            'media_blobs': self.media_blobs,
        }