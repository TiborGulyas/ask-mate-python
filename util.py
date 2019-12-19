from time import time

ALLOWED_extensions = {'png', 'jpg', 'jpeg', 'gif'}


def generate_time():
    return str(int(time()))


def generate_id(data_type):
    data_list = get_data(data_type)
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
        reverse=True if direction == 'desc' else False)
