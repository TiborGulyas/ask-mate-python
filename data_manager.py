from time import time
import connection
import server


def get_data(path):
    if path == 'question':
        file_path = 'sample_data/question.csv'
        header = server.DATA_HEADER_question
    elif path == 'answer':
        file_path = 'sample_data/answer.csv'
        header = server.DATA_HEADER_answer
    output_list = connection.read_file(file_path, header)
    return output_list


def write_data(path, data):
    if path == 'question':
        file_path = 'sample_data/question.csv'
        header = server.DATA_HEADER_question
    elif path == 'answer':
        file_path = 'sample_data/answer.csv'
        header = server.DATA_HEADER_answer
    connection.write_file(file_path, header, data)
