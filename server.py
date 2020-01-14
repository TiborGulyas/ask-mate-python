from flask import Flask, render_template, request, redirect, send_from_directory
import data_manager
import os
import util

app = Flask(__name__, static_url_path='/static')

DATA_HEADER_question = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
DATA_HEADER_answer = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
UPLOAD_folder = './uploaded_image/'
app.config['UPLOAD_FOLDER'] = UPLOAD_folder


@app.route('/', methods=['GET', 'POST'])
@app.route('/list', methods=['GET', 'POST'])
def question_list():
    if request.args:
        args = dict(request.args)
        question_dictionary = data_manager.get_all_questions(args)
        return render_template(
            'list.html',
            question_dictionary_list=question_dictionary,
            direction=args['order_direction'])

    elif request.method == 'GET':
        question_dictionary = data_manager.get_all_questions()
        return render_template(
            'list.html',
            question_dictionary_list=question_dictionary)


@app.route('/question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'GET':
        return render_template('new-question.html')

    elif request.method == "POST":
        new_question = {'title': request.form.get('title'), 'message': request.form.get('message'),
                        'submission_time': util.generate_time(), 'view_number': '0', 'vote_number': '0',
                        'image': 'not found'}
        try:
            file = request.files['file']
            if file and util.allowed_file(file.filename):
                filename_original = file.filename.split('.')
                filename = ".".join([new_question['id'], filename_original[-1]])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_question['image'] = "uploaded-image/" + filename
        except FileNotFoundError:
            pass
        new_question['id'] = data_manager.insert_new_question(*new_question.values())

        return redirect("/question/" + new_question['id'])


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def view_question(question_id):
    if request.method == 'GET' and question_id.isdigit():
        question_for_display = data_manager.get_question_by_id(question_id)
        return render_template(
            'question.html',
            question_for_display=question_for_display)


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    if request.method == 'GET':
        return render_template('add_new_question.html', output_dict=util.get_data_of_editable_question(question_id))
    elif request.method == 'POST':
        try:
            filename = util.generate_file_name_for_image(request.files['file'], question_id)
            request.files['file'].save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        except TypeError:
            filename = ""
        util.update_question(question_id, request.form.get('message'), request.form.get('title'), filename)
        return redirect('/')


@app.route('/question/<question_id>/delete', methods=['GET', 'POST'])
def delete_question(question_id):
    question_dictionary_list = data_manager.get_data('question')
    for number, dict_in_data in enumerate(question_dictionary_list):
        if dict_in_data['id'] == int(question_id):
            try:
                question_dictionary_list[number]['image'] = \
                    list(question_dictionary_list[number]['image'].split('/'))[1]
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], question_dictionary_list[number]['image']))
            except IsADirectoryError:
                pass
            del question_dictionary_list[number]
    data_manager.write_data('question', question_dictionary_list)
    return redirect('/')


@app.route('/question/<question_id>/<vote>', methods=['GET', 'POST'])
def question_vote(question_id, vote):
    question_dictionary_list = data_manager.get_data('question')
    for number, dict_in_data in enumerate(question_dictionary_list):
        if dict_in_data['id'] == int(question_id):
            if vote == "vote_up":
                question_dictionary_list[number]['vote_number'] += 1
            else:
                question_dictionary_list[number]['vote_number'] -= 1
    data_manager.write_data('question', question_dictionary_list)
    return redirect('/')


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def add_answer(question_id):
    question_for_display = util.get_data_of_editable_question(question_id)
    if request.method == 'GET':
        return render_template(
            'new-answer.html',
            question_for_display=question_for_display,
            header=DATA_HEADER_question,
            question_id=question_id)
    elif request.method == "POST":
        new_answer = {'message': request.form.get('message'), 'id': util.generate_id('answer'),
                      'submission_time': util.generate_time(), 'vote_number': '0', 'image': '',
                      'question_id': int(question_id)}
        try:
            file = request.files['file']
            if file and util.allowed_file(file.filename):
                filename_original = file.filename.split('.')
                filename = ".".join(['a', new_answer['id'], filename_original[-1]])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_answer['image'] = "uploaded-image/" + filename
        except FileNotFoundError:
            new_answer['image'] = ''
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


@app.route('/answer/<answer_id>/<vote>', methods=['GET', 'POST'])
def answer_vote(answer_id, vote):
    answer_dictionary_list = data_manager.get_data('answer')
    for number, dict_in_data in enumerate(answer_dictionary_list):
        if dict_in_data['id'] == int(answer_id):
            if vote == "vote_up":
                answer_dictionary_list[number]['vote_number'] += 1
            else:
                answer_dictionary_list[number]['vote_number'] -= 1
            question_id = dict_in_data['question_id']
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
