import sqlite3, os
from itertools import groupby
from operator import itemgetter

from flask import render_template
from flask_login import current_user

from database import Database

def query_into_dict(select_query, params = ''):
    """
    Returns data from an SQL query as a list of dictionaries.
    """
    try:
        db = Database("database.db")
        db.conn.row_factory = sqlite3.Row  # Set row_factory to return dictionaries
        cursor = db.conn.cursor()
        cursor.execute(select_query, params)
        result = cursor.fetchall()
        
        db.conn.commit()
        db.conn.close()

        # Convert each row to a dictionary
        data_list = []
        for row in result:
            data_dict = dict(row)
            data_list.append(data_dict)

        return data_list
    except sqlite3.Error as e:
        print(f"Error fetching data: {e}")
        return []
    

def apology(prompt, status_code = 400):
    return render_template(f'errors/error.html', prompt=prompt, status_code=status_code)


def word_count(string):
    # Remove spaces from start and end, then split into words
    words = string.strip().split(" ")
    return len(words)


def is_allowed_file(file, is_multiple=False, type="image"):
    if type == 'image':
        allowed_list = ['image/jpeg', 'image/png']
    elif type == 'video':
        allowed_list = []

    if is_multiple: 
        for row in file:
            mimetype = row.content_type
            if not mimetype in allowed_list:
                return False
        return True
    else:
        mimetype = file.content_type
        if mimetype in allowed_list:
            return True
        return False


def validate_file_size(image_file, is_multiple=False, max_size_mb=7):
    if is_multiple:
        for file in image_file:
            file_length = file.seek(0, os.SEEK_END) / 1000000
            # Reset the position to zero (to read the file) 
            file.seek(0, os.SEEK_SET)
            if file_length > max_size_mb:
                return False
        return True
    else:
        file_length = image_file.seek(0, os.SEEK_END) / 1000000
        # Reset the position to zero (to read the file) 
        image_file.seek(0, os.SEEK_SET)
        return file_length <= max_size_mb


def upload_image(image_file, column):
    image_data = image_file.read()
    db = Database("database.db")
    db.cursor.execute("UPDATE users SET {} = ? WHERE id = ?".format(column), (sqlite3.Binary(image_data), current_user.id))
    db.conn.commit()

def format_created_at(created_at_day, created_at_second):
    created_at = 'Just now'
    if created_at_day < 1:
        created_at_dict = {
            'second': int(created_at_second),
            'min': int(created_at_second / 60),
            'hour': int(created_at_second / 3600),
        }
        
        for key, value in created_at_dict.items():
            if value == 0:
                break
            created_at = f"{value} " + (key if value == 1 else key + 's') + ' ago'
    else:
        created_at_dict = {
            'day': int(created_at_day),
            'week': int(created_at_day / 7),
            'month': int(created_at_day / 30),
            'year': int(created_at_day / 365)
        }

        for key, value in created_at_dict.items():
            if value == 0:
                break
            created_at = f"{value} " + (key if value == 1 else key + 's') + ' ago'

    return created_at