from flask import Flask, render_template, request, redirect, send_from_directory
import data_manager
import os
import util

app = Flask(__name__, static_url_path='/static')

DATA_HEADER_question = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
DATA_HEADER_answer = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
UPLOAD_folder = 'uploaded_image'
app.config['UPLOAD_FOLDER'] = UPLOAD_folder


@app.route('/', methods=['GET', 'POST'])
def first_five_question_list():
    if request.args:
        args = dict(request.args)
        if 'order_by' in args.keys():
            question_dictionary = data_manager.get_first_five_questions()
            return render_template(
                'list.html',
                question_dictionary_list=question_dictionary,
                direction=args['order_direction'],
                first_five='first five')

    elif request.method == 'POST':
        detail = request.form.get('search')
        return redirect(f"/search?q={detail}")

    elif request.method == 'GET':
        question_dictionary = data_manager.get_first_five_questions()
        return render_template(
            'list.html',
            question_dictionary_list=question_dictionary,
            first_five='first five')


@app.route('/list', methods=['GET', 'POST'])
def question_list():
    if request.args:
        args = dict(request.args)
        if 'order_by' in args.keys():
            print(args)
            question_dictionary = data_manager.get_all_questions(args)
            return render_template(
                'list.html',
                question_dictionary_list=question_dictionary,
                direction=args['order_direction'])

    elif request.method == 'POST':
        detail = request.form.get('search')
        return redirect(f"/search?q={detail}")

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


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
def new_tag(question_id):
    if request.method == 'GET' and question_id.isdigit():
        question_for_display = data_manager.get_question_by_id(question_id)
        tags_already_have = data_manager.get_tags_by_id(question_id)
        all_tags = data_manager.get_all_tags()
        tags_for_choose = [tag for tag in tags_already_have + all_tags if tag not in tags_already_have or tag not in all_tags]
        number_of_tags = len(tags_for_choose)
        return render_template('add-tag.html', question_id=question_id,
            question_for_display=question_for_display, tags_for_choose=tags_for_choose, number_of_tags=number_of_tags)

    elif request.method == 'POST':
        if request.form.get('submit_new_tag') != "":
            new_tag = {'new_tag': request.form.get('submit_new_tag')}
            data_manager.save_new_tag(new_tag['new_tag'])
            data_manager.save_tag_for_question(new_tag['new_tag'], question_id)
            return redirect('/list')
        elif request.form.get('submit_new_tag') == "":
            new_tag = {'new_tag': request.form.get('submit_existing_tag')}
            data_manager.save_tag_for_question(new_tag['new_tag'], question_id)
            return redirect('/list')



@app.route('/question/<question_id>', methods=['GET', 'POST'])
def view_question(question_id):
    if request.method == 'GET' and question_id.isdigit():
        question_for_display = data_manager.get_question_by_id(question_id)
        answer_for_display = data_manager.get_answer_by_question_id(question_id)
        question_comment_for_display = data_manager.get_comment_by_id(question_id)
        answer_comment_for_display = data_manager.get_all_comments()
        answer_with_comment = []
        for answer in answer_for_display:
            for comment in answer_comment_for_display:
                if answer['id'] == comment['answer_id']:
                    answer_with_comment.append(answer['id'])
        tags_for_display = data_manager.get_tags_by_id(question_id)
        number_of_tags = len(tags_for_display)
        if len(answer_for_display) == 0:
            answer_for_display = [{'message': 'No answer yet', 'submission_time': '', 'vote_number': '', 'image': ''}]
        return render_template(
            'question.html', question_id=question_id,
            question_for_display=question_for_display, answer_for_display=answer_for_display, tags_for_display=tags_for_display, number_of_tags=number_of_tags, question_comment_for_display=question_comment_for_display, answer_comment_for_display=answer_comment_for_display, answer_with_comment=answer_with_comment)


@app.route('/question/<question_id>/tag/<tag_id>/delete', methods=['GET', 'POST'])
def delete_tag(question_id, tag_id):
    if request.method == 'GET':
        data_manager.delete_tag(question_id,tag_id)
        return redirect(f'/question/{question_id}')


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
        data_manager.update_question(question_id, request.form.get('message'), request.form.get('title'), image,
                                     util.generate_time())
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
        data_manager.update_answer(new_answer_id, new_answer['message'], new_answer['image'],
                                   new_answer['submission_time'])
        return redirect(f'/question/{question_id}')


@app.route('/answer/<answer_id>', methods=['GET', 'POST'])
def show_answer(answer_id):
    answer_for_display = data_manager.get_answer_by_id(answer_id)
    return render_template('answer.html', answer_for_display=answer_for_display[0])


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(answer_id):
    if request.method == 'GET':
        answer_for_display = data_manager.get_answer_by_id(answer_id)
        print(answer_for_display[0])
        question_for_display = data_manager.get_question_by_id(answer_for_display[0]['question_id'])
        return render_template('new-answer.html', output_dict=answer_for_display[0],
                               question_for_display=question_for_display)
    elif request.method == 'POST':
        image = 'not found'
        try:
            file = request.files['file']
            if file and util.allowed_file(file.filename):
                filename_original = file.filename.split('.')
                filename = ".".join(['a', answer_id, filename_original[-1]])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = "uploaded-image/" + filename
        except TypeError:
            image = 'TypeError'
        data_manager.update_answer(answer_id, request.form.get('message'), image, util.generate_time())
        question_id = data_manager.get_answer_by_id(answer_id)[0]['question_id']
        return redirect(f'/question/{question_id}')


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


@app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
def add_question_comment(question_id):
    question_for_display = data_manager.get_question_by_id(question_id)
    if request.method == 'GET':
        return render_template(
            'new-comment.html',
            question_for_display=question_for_display)

    elif request.method == 'POST':
        new_comment = {'id_type': 'question_id',
                       'question_id': int(question_id),
                       'message': request.form.get('comment'),
                       'submission_time': util.generate_time(),
                       'edited_count': '0'}

        data_manager.insert_new_comment(*new_comment.values())
        return redirect(f'/question/{question_id}')


@app.route('/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
def add_answer_comment(answer_id):
    answer_for_display = data_manager.get_answer_by_id(answer_id)
    if request.method == 'GET':
        return render_template(
            'new-comment.html',
            answer_for_display=answer_for_display[0])

    elif request.method == 'POST':
        new_comment = {'id_type': 'answer_id',
                       'answer_id': int(answer_id),
                       'message': request.form.get('comment'),
                       'submission_time': util.generate_time(),
                       'edited_count': '0'}

        print(new_comment.values())
        data_manager.insert_new_comment(*new_comment.values())
        return redirect(f'/question/{answer_for_display[0]["question_id"]}')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        detail = request.form.get('search')
        return redirect(f"/search?q={detail}")
    detail = dict(request.args)['q']
    questions = data_manager.get_question_by_search(detail)
    question_ids = data_manager.get_question_ids_by_search_from_answers(detail)
    for question in question_ids:
        found_question = data_manager.get_question_by_id(question['question_id'])
        if found_question not in questions:
            questions.append(found_question)
    print(questions)
    questions = fancy_search(questions, detail)
    return render_template(
        'list.html', question_dictionary_list=questions)


def fancy_search(questions, detail):
    for row in questions:
        row['message'] = str(row['message']).replace(f"{detail}", f"<b>{detail}</b>")
    return questions


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
