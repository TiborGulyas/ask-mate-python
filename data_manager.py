import csv

DATA_HEADER_question = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
DATA_HEADER_answer = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def get_data(path):
    output_list = []
    if path == 'question':
        file_path = 'sample_data/question.csv'
        header = DATA_HEADER_question
    elif path == 'answer':
        file_path = 'sample_data/answer.csv'
        header = DATA_HEADER_answer
    with open(file_path, newline='') as source_file:
        source_list = csv.DictReader(source_file, delimiter=",")
        for line in source_list:
            source_dictionary = {}
            for source_header in header:
                try:
                    source_dictionary[source_header] = int(line[source_header])
                except ValueError:
                    source_dictionary[source_header] = line[source_header]
            output_list.append(source_dictionary)
    return output_list
