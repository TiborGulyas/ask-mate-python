from flask import Flask, render_template, request, redirect, url_for
import data_manager
app = Flask(__name__)

DATA_HEADER_question = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
DATA_HEADER_answer = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


@app.route('/', methods=['GET', 'POST'])
@app.route('/list', methods=['GET', 'POST'])
def question_list():
    if request.method == 'GET':
        sort_by = 'id'
        question_dictionary_list = data_manager.get_data('question')
        sorted_question_dictionary_list = sorted(question_dictionary_list, key=lambda question: question[sort_by])
        return render_template('list.html', question_dictionary_list=sorted_question_dictionary_list, header=DATA_HEADER_question)


@app.route('/question', methods=['GET', 'POST'])
@app.route('/question/<question_id>', methods=['GET', 'POST'])
def add_question(question_id = 'None'):
    if question_id.isdigit() == True and request.method == 'GET':
        question_dictionary_list = data_manager.get_data('question')
        answer_dictionary_list = data_manager.get_data('answer')
        answer_for_display = []
        for question in question_dictionary_list:
            if int(question['id']) == int(question_id):
                question_for_display = question
        for answer in answer_dictionary_list:
            if int(answer['question_id']) == int(question_id):
                answer_for_display.append(answer)
        return render_template('question.html', question_for_display=question_for_display, header=DATA_HEADER_question, answer_for_display=answer_for_display, answer_header=DATA_HEADER_answer)

    elif request.method == 'GET':
        return render_template('add_new_question.html')

    elif request.method == "POST":
        new_question = {
            'title': request.form.get('title'),
            'message': request.form.get('message'),
        }
        new_question['id'] = data_manager.generate_id('question')
        new_question['submission_time'] = data_manager.generate_time()
        new_question['view_number'] = '0'
        new_question['vote_number'] = '0'
        new_question['image'] = ''
        question_dictionary_list = data_manager.get_data('question')
        question_dictionary_list.append(new_question)
        data_manager.write_data('question', question_dictionary_list)
        return render_template('question.html', question_for_display=new_question, header=DATA_HEADER_question)





if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )