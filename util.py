import datetime
from flask import session
import data_manager
import bcrypt

ALLOWED_extensions = {'png', 'jpg', 'jpeg', 'gif'}


def generate_time():
    date = str(datetime.datetime.today())
    date = date[:-6]
    date += "000000"
    return date


def generate_id(data_type):
    data_list = data_manager.get_data(data_type)
    id_list = []
    for ids in data_list:
        id_list.append(int(ids['id']))
    if not id_list:
        return "0"
    else:
        new_id = max(id_list) + 1
        return str(new_id)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_extensions


def sort_by_type(data, data_type, direction):
    return sorted(
        data,
        key=lambda question: question[data_type],
        reverse=True if direction == 'desc' else False
    )


def get_data_of_editable_question(question_id):
    data = data_manager.get_data('question')
    for dict_in_data in data:
        if dict_in_data['id'] == int(question_id):
            return dict_in_data


def generate_file_name_for_image(file, question_id):
    if file and allowed_file(file.filename):
        filename_original = file.filename.split('.')
        return ".".join([question_id, filename_original[-1]])


def update_question(question_id, message, title, filename):
    question_dictionary_list = data_manager.get_data('question')
    for number, dict_in_data in enumerate(question_dictionary_list):
        if dict_in_data['id'] == int(question_id):
            question_dictionary_list[number]['message'] = message
            question_dictionary_list[number]['title'] = title
            question_dictionary_list[number]['submission_time'] = generate_time()
            question_dictionary_list[number]['image'] = "uploaded-image/" + filename
    data_manager.write_data('question', question_dictionary_list)


def hash_password(plain_text_password):
    # By using bcrypt, the salt is saved into the hash itself
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def validate_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)

def return_user():
    try:
        return session['username']
    except KeyError:
        return 'not logged in'