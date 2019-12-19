from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import data_manager
import os
from werkzeug.utils import secure_filename
app = Flask(__name__, static_url_path='/static')

DATA_HEADER_question = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
DATA_HEADER_answer = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
UPLOAD_folder = '/home/nkornel/codecool/02_Web/01_TW/ask-mate-python/uploaded_image/'
ALLOWED_extensions = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_folder


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_extensions


@app.route('/', methods=['GET', 'POST'])
@app.route('/list', methods=['GET', 'POST'])
def question_list():
    if request.args:
        args = dict(request.args)
        direction = args['order_direction']
        question_dictionary_list = data_manager.get_data('question')
        sorted_question_dictionary_list = sorted(question_dictionary_list, key=lambda question: question[args['order_by']], reverse=True if direction == "desc" else False)
        return render_template('list.html', question_dictionary_list=sorted_question_dictionary_list, header=DATA_HEADER_question, direction=direction)
    elif request.method == 'GET':
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
        for number, question in enumerate(question_dictionary_list):
            if int(question['id']) == int(question_id):
                question_for_display = question
                question_dictionary_list[number]['view_number'] += 1
        for answer in answer_dictionary_list:
            if int(answer['question_id']) == int(question_id):
                answer_for_display.append(answer)
        data_manager.write_data('question', question_dictionary_list)
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
        return redirect("/question/" + new_question['id'])

#        return render_template('question.html', question_for_display=new_question, header=DATA_HEADER_question)


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def add_answer(question_id):
    question_dictionary_list = data_manager.get_data('question')
    for question in question_dictionary_list:
        if int(question['id']) == int(question_id):
            question_for_display = question
    if request.method == 'GET':
        return render_template('new-answer.html', question_for_display=question_for_display, header=DATA_HEADER_question, question_id=question_id)
    elif request.method == "POST":
        new_answer = {
            'message': request.form.get('message'),
        }
        new_answer['id'] = data_manager.generate_id('answer')
        new_answer['submission_time'] = data_manager.generate_time()
        new_answer['vote_number'] = '0'
        new_answer['image'] = ''
        new_answer['question_id'] = int(question_id)
        answer_dictionary_list = data_manager.get_data('answer')
        answer_dictionary_list.append(new_answer)
        data_manager.write_data('answer', answer_dictionary_list)
        answer_dictionary_list = data_manager.get_data('answer')
        answer_for_display = []
        for answer in answer_dictionary_list:
            if int(answer['question_id']) == int(question_id):
                answer_for_display.append(answer)
        return redirect(f'/question/{question_id}')


@app.route('/answer/<answer_id>', methods=['GET', 'POST'])
def show_answer(answer_id):
    for answer in data_manager.get_data('answer'):
        if answer['id'] == int(answer_id):
            answer_for_display = answer
    return render_template('answer.html', answer_for_display=answer_for_display, answer_header=DATA_HEADER_answer)


@app.route('/answer/<answer_id>/delete', methods=['GET', 'POST'])
def delete_answer(answer_id):
    answer_dictionary_list = data_manager.get_data('answer')
    for number, dict in enumerate(answer_dictionary_list):
        if dict['id'] == int(answer_id):
            del answer_dictionary_list[number]
    data_manager.write_data('answer', answer_dictionary_list)
    return redirect('/')


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id, output_dict='None'):
    if request.method == 'GET':
        data = data_manager.get_data('question')
        for dict in data:
            if dict['id'] == int(question_id):
                output_dict = dict
        return render_template('add_new_question.html', output_dict=output_dict)
    elif request.method == 'POST':
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file and allowed_file(file.filename):
            filename_original = file.filename.split('.')
            filename = ".".join([question_id, filename_original[-1]])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        question_dictionary_list = data_manager.get_data('question')
        for number, dict in enumerate(question_dictionary_list):
            if dict['id'] == int(request.form.get('id')):
                question_dictionary_list[number]['message'] = request.form.get('message')
                question_dictionary_list[number]['title'] = request.form.get('title')
                question_dictionary_list[number]['submission_time'] = data_manager.generate_time()
                question_dictionary_list[number]['image'] = "uploaded-image/" + filename
        data_manager.write_data('question', question_dictionary_list)
        return redirect('/')


@app.route('/question/<question_id>/delete', methods=['GET', 'POST'])
def delete_question(question_id):
    question_dictionary_list = data_manager.get_data('question')
    for number, dict in enumerate(question_dictionary_list):
        if dict['id'] == int(question_id):
            try:
                question_dictionary_list[number]['image'] = list(question_dictionary_list[number]['image'].split('/'))[1]
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], question_dictionary_list[number]['image']))
            except IndexError:
                pass
            del question_dictionary_list[number]
    data_manager.write_data('question', question_dictionary_list)
    return redirect('/')


@app.route('/question/<question_id>/<vote>', methods=['GET', 'POST'])
def question_vote(question_id, vote):
    question_dictionary_list = data_manager.get_data('question')
    for number, dict in enumerate(question_dictionary_list):
        if dict['id'] == int(question_id):
            if vote == "vote_up":
                question_dictionary_list[number]['vote_number'] += 1
            else:
                question_dictionary_list[number]['vote_number'] -= 1
    data_manager.write_data('question', question_dictionary_list)
    return redirect('/')


@app.route('/answer/<answer_id>/<vote>', methods=['GET', 'POST'])
def answer_vote(answer_id, vote):
    answer_dictionary_list = data_manager.get_data('answer')
    for number, dict in enumerate(answer_dictionary_list):
        if dict['id'] == int(answer_id):
            if vote == "vote_up":
                answer_dictionary_list[number]['vote_number'] += 1
            else:
                answer_dictionary_list[number]['vote_number'] -= 1
            question_id = dict['question_id']
    data_manager.write_data('answer', answer_dictionary_list)
    return redirect(f'/question/{question_id}')


@app.route('/uploaded-image/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )