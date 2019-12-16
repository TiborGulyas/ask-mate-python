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








if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )