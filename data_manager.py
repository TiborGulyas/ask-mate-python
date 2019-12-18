from time import time
import connection

DATA_HEADER_question = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
DATA_HEADER_answer = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def get_data(path):
    if path == 'question':
        file_path = 'sample_data/question.csv'
        header = DATA_HEADER_question
    elif path == 'answer':
        file_path = 'sample_data/answer.csv'
        header = DATA_HEADER_answer
    output_list = connection.read_file(file_path,header)
    return output_list


def write_data(path, data):
    if path == 'question':
        file_path = 'sample_data/question.csv'
        header = DATA_HEADER_question
    elif path == 'answer':
        file_path = 'sample_data/answer.csv'
        header = DATA_HEADER_answer
    connection.write_file(file_path, header, data)


def generate_id(type):
    list = get_data(type)
    id_list = []
    for ids in list:
        id_list.append(ids['id'])
    if not id_list:
        return "0"
    else:
        new_id = max(id_list) + 1
        return str(new_id)


def generate_time():
    t = int(time())
    return str(t)