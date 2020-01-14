from flask import Flask, render_template, request, redirect, send_from_directory
import data_manager
import os
import util

app = Flask(__name__, static_url_path='/static')

DATA_HEADER_question = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
DATA_HEADER_answer = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
UPLOAD_folder = 'uploaded_image'
print(app.config)
app.config['UPLOAD_FOLDER'] = UPLOAD_folder
print(app.config)


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
        new_question['id'] = data_manager.insert_new_question(*new_question.values())
        try:
            file = request.files['file']
            if file and util.allowed_file(file.filename):
                filename_original = file.filename.split('.')
                filename = ".".join([new_question['id'], filename_original[-1]])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_question['image'] = "uploaded-image/" + filename
        except FileNotFoundError:
            pass
        data_manager.insert_image(new_question['id'], 'question', new_question['image'])
        return redirect("/question/" + new_question['id'])


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def view_question(question_id):
    if request.method == 'GET' and question_id.isdigit():
        question_for_display = data_manager.get_question_by_id(question_id)
        answer_for_display = data_manager.get_answer_by_question_id(question_id)
        if len(answer_for_display) == 0:
            answer_for_display = [{'message': 'No answer yet', 'submission_time': '', 'vote_number': '', 'image': ''}]
        return render_template(
            'question.html',
            question_for_display=question_for_display, answer_for_display=answer_for_display)


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    if request.method == 'GET':
        return render_template('new-question.html', output_dict=data_manager.get_question_by_id(question_id))
    elif request.method == 'POST':
        filename = 'not found'
        try:
            file = request.files['file']
            if file and util.allowed_file(file.filename):
                filename_original = file.filename.split('.')
                filename = ".".join([question_id, filename_original[-1]])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = "uploaded-image/" + filename
        except TypeError:
            filename = 'TypeError'
        data_manager.update_question(question_id, request.form.get('message'), request.form.get('title'), image, util.generate_time())
        return redirect('/')


@app.route('/question/<question_id>/delete', methods=['GET', 'POST'])
def delete_question(question_id):
    data_manager.delete_question(question_id)
    return redirect('/')


@app.route('/question/<question_id>/<vote>', methods=['GET', 'POST'])
def question_vote(question_id, vote):
    if vote == "vote_up":
        data_manager.vote_question(question_id, 1)
    else:
        data_manager.vote_question(question_id, -1)
    return redirect('/')


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def add_answer(question_id):
    question_for_display = data_manager.get_question_by_id(question_id)
    if request.method == 'GET':
        return render_template(
            'new-answer.html',
            question_for_display=question_for_display,
            question_id=question_id)
    elif request.method == "POST":
        new_answer = {'message': request.form.get('message'),
                      'submission_time': util.generate_time(), 'vote_number': '0', 'question_id': int(question_id),
                      'image': 'not found'}
        print(new_answer)
        new_answer_id = data_manager.insert_new_answer(*new_answer.values())
        try:
            file = request.files['file']
            if file and util.allowed_file(file.filename):
                filename_original = file.filename.split('.')
                filename = ".".join([new_answer_id, filename_original[-1]])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_answer['image'] = "uploaded-image/" + filename
        except FileNotFoundError:
            pass
        print(*new_answer.values())
        data_manager.insert_new_answer(*new_answer.values())
        return redirect(f'/question/{question_id}')


@app.route('/answer/<answer_id>', methods=['GET', 'POST'])
def show_answer(answer_id):
    answer_for_display = data_manager.get_answer_by_id(answer_id)
    return render_template('answer.html', answer_for_display=answer_for_display[0])


@app.route('/answer/<answer_id>/delete', methods=['GET', 'POST'])
def delete_answer(answer_id):
    question_id = data_manager.delete_answer(answer_id)
    return redirect(f'/question/{question_id}')


@app.route('/answer/<answer_id>/<vote>', methods=['GET', 'POST'])
def answer_vote(answer_id, vote):
    if vote == "vote_up":
        question_id = data_manager.vote_answer(answer_id, 1)
    else:
        question_id = data_manager.vote_answer(answer_id, -1)
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
