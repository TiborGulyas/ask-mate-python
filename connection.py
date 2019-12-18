import csv

def read_file(file_path,header):
    output_list = []
    with open(file_path, newline='') as source_file:
        for line in csv.DictReader(source_file, delimiter=","):
            source_dictionary = {}
            for source_header in header:
                if source_header == 'id' or source_header == 'submission_time' or source_header == 'view_number' or source_header == 'vote_number' or source_header == 'question_id':
                    source_dictionary[source_header] = int(line[source_header])
                else:
                    source_dictionary[source_header] = line[source_header]
            output_list.append(source_dictionary)
    return output_list


def write_file(file_path, header, data):
    with open(file_path, 'w', newline='') as source_file:
        fieldnames = header
        writer = csv.DictWriter(source_file, fieldnames=fieldnames)
        writer.writeheader()
        print(data)
        for question in data:
            writer.writerow(question)