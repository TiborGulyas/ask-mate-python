from flask import Flask, render_template, request, redirect, send_from_directory, session, escape
import data_manager
import os
import util
import uuid

app = Flask(__name__, static_url_path='/static')

DATA_HEADER_question = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
DATA_HEADER_answer = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
UPLOAD_folder = 'uploaded_image'
app.config['UPLOAD_FOLDER'] = UPLOAD_folder
actual_sessions = {}


@app.route('/', methods=['GET', 'POST'])
def first_five_question_list():
    user = util.return_user()
    user_id = data_manager.get_user_id_by_user_name(user)
    vote_history = data_manager.get_vote_history('question', user_id)
    if request.args:
        args = dict(request.args)
        if 'order_by' in args.keys():
            question_dictionary = data_manager.get_first_five_questions()
            return render_template(
                'list.html',
                question_dictionary_list=question_dictionary,
                direction=args['order_direction'],
                first_five='first five',
                user=user, user_id=user_id, vote_history=vote_history)

    elif request.method == 'POST':
        detail = request.form.get('search')
        return redirect(f"/search?q={detail}")

    elif request.method == 'GET':
        question_dictionary = data_manager.get_first_five_questions()
        return render_template(
            'list.html',
            question_dictionary_list=question_dictionary,
            first_five='first five',
            user=user, user_id=user_id, vote_history=vote_history)


@app.route('/list', methods=['GET', 'POST'])
def question_list():
    user = util.return_user()
    user_id = data_manager.get_user_id_by_user_name(user)
    vote_history = data_manager.get_vote_history('question', user_id)
    if request.args:
        args = dict(request.args)
        if 'order_by' in args.keys():
            question_dictionary = data_manager.get_all_questions(args)
            return render_template(
                'list.html',
                question_dictionary_list=question_dictionary,
                direction=args['order_direction'],
                user=user, user_id=user_id, vote_history=vote_history)

    elif request.method == 'POST':
        detail = request.form.get('search')
        return redirect(f"/search?q={detail}")

    elif request.method == 'GET':
        question_dictionary = data_manager.get_all_questions()
        return render_template(
            'list.html',
            question_dictionary_list=question_dictionary,
            user=user, user_id=user_id, vote_history=vote_history)


@app.route('/question', methods=['GET', 'POST'])
def add_question():
    user = util.return_user()
    if request.method == 'GET':
        if 'username' in session:
            return render_template('new-question.html', user=user)
        return render_template('access-error.html', data_type='add_new_question')
    elif request.method == "POST":
        user_id = data_manager.get_user_id_by_user_name(session['username'])
        new_question = {'title': request.form.get('title'), 'message': request.form.get('message'),
                        'submission_time': util.generate_time(), 'view_number': '-1', 'vote_number': '0',
                        'image': 'not found', 'user_id': user_id}
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
        data_manager.insert_image_question(new_question['id'], new_question['image'])
        return redirect("/question/" + new_question['id'])


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
def new_tag(question_id):
    user = util.return_user()
    if request.method == 'GET' and question_id.isdigit():
        if 'username' in session:
            question_for_display = data_manager.get_question_by_id(question_id)
            tags_already_have = data_manager.get_tags_by_id(question_id)
            all_tags = data_manager.get_all_tags()
            tags_for_choose = [tag for tag in tags_already_have + all_tags if
                               tag not in tags_already_have or tag not in all_tags]
            number_of_tags = len(all_tags)
            return render_template('add-tag.html', question_id=question_id,
                                   question_for_display=question_for_display, tags_for_choose=all_tags,
                                   number_of_tags=number_of_tags,
                                   tags_for_display=tags_already_have,
                                   user=user)
        return render_template('access-error.html', data_type='add_new_tag', question_id=question_id)

    elif request.method == 'POST':
        if request.form.get('submit_new_tag') != "":
            new_tag = {'new_tag': request.form.get('submit_new_tag')}
            tags = data_manager.get_all_tags()
            inside = False
            for tag in tags:
                if tag['name'] == new_tag['new_tag']:
                    inside = True
            if inside is False:
                data_manager.save_new_tag(new_tag['new_tag'])
            tags_already_have = data_manager.get_tags_by_id(question_id)
            used = False
            if tags_already_have != []:
                for tag in tags_already_have:
                    if tag['name'] == new_tag['new_tag']:
                        used = True
            if not used:
                data_manager.save_tag_for_question(new_tag['new_tag'], question_id)
            return redirect('/list')
        else:
            new_tag = {'new_tag': request.form.get('tags')}
            tags_already_have = data_manager.get_tags_by_id(question_id)
            used = False
            if tags_already_have != []:
                for tag in tags_already_have:
                    if tag['name'] == new_tag['new_tag']:
                        used = True
            if not used:
                data_manager.save_tag_for_question(new_tag['new_tag'], question_id)
            return redirect('/list')


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def view_question(question_id):
    user_id = data_manager.get_user_id_by_question_id(question_id)
    actual_user_id = 'a'

    if 'username' in session:
        actual_user_id = data_manager.get_user_id_by_user_name(session['username'])

    show_answer_accept = False

    if actual_user_id == user_id:
        show_answer_accept = True

    user = util.return_user()
    user_id = data_manager.get_user_id_by_user_name(user)
    try:
        data_manager.view_question(question_id)
    except TypeError:
        pass
    if request.method == 'GET' and question_id.isdigit():
        question_for_display = data_manager.get_question_by_id(question_id)
        answer_for_display = data_manager.get_answer_by_question_id(question_id)
        question_comment_for_display = data_manager.get_comment_by_question_id(question_id)
        answer_comment_for_display = data_manager.get_all_comments()
        answer_with_comment = set()
        vote_history = data_manager.get_vote_history('answer', user_id)
        for answer in answer_for_display:
            for comment in answer_comment_for_display:
                if answer['id'] == comment['answer_id']:
                    answer_with_comment.add(answer['id'])
        tags_for_display = data_manager.get_tags_by_id(question_id)
        number_of_tags = len(tags_for_display)
        if len(answer_for_display) == 0:
            answer_for_display = False

        return render_template(
            'question.html', question_id=question_id,
            question_for_display=question_for_display, answer_for_display=answer_for_display,
            tags_for_display=tags_for_display, number_of_tags=number_of_tags,
            question_comment_for_display=question_comment_for_display,
            answer_comment_for_display=answer_comment_for_display, answer_with_comment=answer_with_comment,
            user=user, user_id=user_id, vote_history=vote_history)


@app.route('/question/<question_id>/tag/<tag_id>/delete', methods=['GET', 'POST'])
def delete_tag(question_id, tag_id):
    if request.method == 'GET':
        data_manager.delete_tag(question_id, tag_id)
        return redirect(f'/question/{question_id}')


@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    user = util.return_user()
    logged_in_user_id = data_manager.get_user_id_by_user_name(user)
    question_user_id = data_manager.get_user_id_by_question_id(question_id)
    if request.method == 'GET':
        if user == 'admin':
            return render_template('new-question.html', output_dict=data_manager.get_question_by_id(question_id), user=user)
        elif 'username' in session and logged_in_user_id == question_user_id:
            return render_template('new-question.html', output_dict=data_manager.get_question_by_id(question_id), user=user)
        return render_template('access-error.html', data_type='edit_question', question_id=question_id)
    elif request.method == 'POST':
        image = 'not found'
        try:
            file = request.files['file']
            if file and util.allowed_file(file.filename):
                filename_original = file.filename.split('.')
                filename = ".".join([question_id, filename_original[-1]])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = "uploaded-image/" + filename
        except TypeError:
            filename = 'TypeError'
        data_manager.update_question(question_id, request.form.get('title'), request.form.get('message'), image,
                                     util.generate_time())
        return redirect('/')


@app.route('/question/<int:question_id>/delete', methods=['GET', 'POST'])
def delete_question(question_id):
    tag_id = data_manager.get_tag_id(question_id)
    user = util.return_user()
    logged_in_user_id = data_manager.get_user_id_by_user_name(user)
    question_user_id = data_manager.get_user_id_by_question_id(question_id)
    if user == 'admin'or logged_in_user_id == question_user_id:
        if tag_id != []:
            for individual_tag in tag_id:
                delete_tag(question_id, individual_tag['tag_id'])
        data_manager.delete_comment_by_question_id(question_id)
        answer_id_set = set()
        answer_list = data_manager.get_answer_by_question_id(question_id)
        for answer in answer_list:
            answer_id_set.add(answer['id'])
        if len(answer_id_set) > 0:
            for answer_id in answer_id_set:
                data_manager.delete_comment_by_answer_id(answer_id)
                data_manager.delete_answer(answer_id)
        data_manager.delete_question(question_id)
        return redirect('/')
    return render_template('access-error.html', data_type='delete_question', question_id=question_id)


@app.route('/question/<question_id>/<vote>', methods=['GET', 'POST'])
def question_vote(question_id, vote):
    user_id = data_manager.get_user_id_by_user_name(util.return_user())
    if vote == "vote_up":
        data_manager.vote_question(question_id, 5)
    else:
        data_manager.vote_question(question_id, -2)
    data_manager.update_vote_history('question', question_id, user_id)
    data_manager.set_reputation(data_manager.get_user_id_by_question_id(question_id))
    return redirect('/')


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def add_answer(question_id):
    user = util.return_user()
    question_for_display = data_manager.get_question_by_id(question_id)
    if request.method == 'GET':

        if 'username' in session:
            return render_template(
                'new-answer.html',
                question_for_display=question_for_display,
                question_id=question_id,
                user=user)
        return render_template('access-error.html', data_type="question", id=question_id)


    elif request.method == "POST":
        user_id = data_manager.get_user_id_by_user_name(session['username'])
        new_answer = {'message': request.form.get('message'),
                      'submission_time': util.generate_time(), 'vote_number': '0', 'question_id': int(question_id),
                      'image': 'not found', 'user_id': user_id}
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
    user = util.return_user()
    question_id = data_manager.get_question_id_by_answer_id(answer_id)
    user_id = data_manager.get_user_id_by_question_id(question_id)
    actual_user_id = 'a'

    if 'username' in session:
        actual_user_id = data_manager.get_user_id_by_user_name(session['username'])

    show_answer_accept = False

    if actual_user_id == user_id:
        show_answer_accept = True

    answer_for_display = data_manager.get_answer_by_id(answer_id)
    return render_template('answer.html', answer_for_display=answer_for_display[0], user=user,
                           show_answer_accept=show_answer_accept)



@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(answer_id):
    user = util.return_user()
    if request.method == 'GET':
        answer_for_display = data_manager.get_answer_by_id(answer_id)

        if 'username' in session:
            user = data_manager.get_user_id_by_user_name(session['username'])
            owner = answer_for_display[0]['user_id']
            if user == owner:
                question_for_display = data_manager.get_question_by_id(answer_for_display[0]['question_id'])
                return render_template('new-answer.html', output_dict=answer_for_display[0],
                                       question_for_display=question_for_display, user=user)
        return render_template('access-error.html', data_type="answer", id=answer_id)


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
    if 'username' in session:
        user = data_manager.get_user_id_by_user_name(session['username'])
        owner = data_manager.get_answer_by_id(answer_id)[0]['user_id']
        if user == owner:
            question_id = data_manager.get_answer_by_id(answer_id)[0]['question_id']
            data_manager.delete_comment_by_answer_id(answer_id)
            data_manager.delete_answer(answer_id)
            return redirect(f'/question/{question_id}')
    return render_template('access-error.html', data_type="answer", id=answer_id)


@app.route('/answer/<answer_id>/<vote>', methods=['GET', 'POST'])
def answer_vote(answer_id, vote):

    if 'username' in session:
        user_id = data_manager.get_user_id_by_user_name(util.return_user())
        if vote == "vote_up":
            question_id = data_manager.vote_answer(answer_id, 10)
        else:
            question_id = data_manager.vote_answer(answer_id, -2)
        data_manager.set_reputation(data_manager.get_user_id_by_answer_id(answer_id))
        data_manager.update_vote_history('answer', answer_id, user_id)
        return redirect(f'/question/{question_id}')
    return render_template('access-error.html', data_type="answer", id=answer_id)


@app.route('/uploaded-image/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
def add_question_comment(question_id):
    user = util.return_user()
    question_for_display = data_manager.get_question_by_id(question_id)
    if request.method == 'GET':
        if 'username' in session:
            return render_template(
                'new-comment.html',
                question_for_display=question_for_display,
                user=user)
        return render_template('access-error.html', data_type="add_new_comment_to_question", question_id=question_id)
    elif request.method == 'POST':
        user_id = data_manager.get_user_id_by_user_name(session['username'])
        new_comment = {'id_type': 'question_id',
                       'question_id': int(question_id),
                       'message': request.form.get('comment'),
                       'submission_time': util.generate_time(),
                       'edited_count': '0','user_id': user_id}

        data_manager.insert_new_comment(*new_comment.values())
        return redirect(f'/question/{question_id}')


@app.route('/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
def add_answer_comment(answer_id):
    answer_for_display = data_manager.get_answer_by_id(answer_id)
    user = util.return_user()
    if request.method == 'GET' and 'username' in session:
        return render_template(
            'new-comment.html',
            answer_for_display=answer_for_display[0],
            user=user)

    elif request.method == 'GET':
        return render_template('access-error.html', data_type="answer", id=answer_id)

    elif request.method == 'POST' and 'username' in session:
        user_id = data_manager.get_user_id_by_user_name(session['username'])
        new_comment = {'id_type': 'answer_id',
                       'answer_id': int(answer_id),
                       'message': request.form.get('comment'),
                       'submission_time': util.generate_time(),
                       'edited_count': '0', 'user_id': user_id}

        data_manager.insert_new_comment(*new_comment.values())
        return redirect(f'/question/{answer_for_display[0]["question_id"]}')


@app.route('/search', methods=['GET', 'POST'])
def search():
    user = util.return_user()
    if request.method == 'POST':
        detail = request.form.get('search')
        return redirect(f"/search?q={detail}")
    detail = dict(request.args)['q']
    questions = data_manager.get_question_by_search(detail)
    answers = data_manager.get_question_ids_by_search_from_answers(detail)
    question_ids = set()
    for answer in answers:
        question_ids.add(answer['question_id'])
        found_question = data_manager.get_question_by_id(answer['question_id'])
        if found_question not in questions:
            questions.append(found_question)
    questions = fancy_search(questions, detail)
    answers = fancy_search(answers, detail)
    if len(questions) < 1:
        return redirect('/', user=user)
    return render_template(
        'list.html', question_dictionary_list=questions, answer_dictionary_list=answers, question_ids=question_ids,
        search=True, user=user)


def fancy_search(questions, detail):
    for row in questions:
        row['message'] = str(row['message']).replace('<', '&lt;').replace('>', '&gt;').replace(
            f"{detail.replace('<', '&lt;').replace('>', '&gt;')}",
            f"<strong>{detail.replace('<', '&lt;').replace('>', '&gt;')}</strong>")
        try:
            row['title'] = str(row['title']).replace('<', '&lt;').replace('>', '&gt;').replace(
                f"{detail.replace('<', '&lt;').replace('>', '&gt;')}",
                f"<strong>{detail.replace('<', '&lt;').replace('>', '&gt;')}</strong>")
        except KeyError:
            pass
    return questions


@app.route('/comment/<comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    actual_question = data_manager.get_question_id_by_comment_id(comment_id)
    actual_answer = data_manager.get_answer_id_by_comment_id(comment_id)
    actual_user_id = 'nothing'
    if 'username' in session:
        actual_user_id = data_manager.get_user_id_by_user_name(session['username'])

    comment_user_id = data_manager.get_user_by_comment_id(comment_id)

    if request.method == 'GET' and actual_user_id == comment_user_id:
        user = util.return_user()
        comment_type = ""
        all_comments = data_manager.get_all_comments()
        for comment in all_comments:
            if int(comment['id']) == int(comment_id):
                if comment['question_id'] is None:
                    comment_type = 'answer'
                    comment_for_display = comment
                    answer_id = comment['answer_id']
                else:
                    comment_type = 'question'
                    comment_for_display = comment
                    question_id = comment['question_id']
        if request.method == 'GET' and comment_type == 'answer':
            answer_for_display = data_manager.get_answer_by_id(answer_id)
            return render_template(
                'new-comment.html',
                answer_for_display=answer_for_display[0], comment_type=comment_type,
                comment_for_display=comment_for_display,
                user=user)

        if request.method == 'GET' and comment_type == 'question':
            question_for_display = dict(data_manager.get_question_by_id(question_id))
            return render_template(
                'new-comment.html',
                question_for_display=question_for_display, comment_type=comment_type,
                comment_for_display=comment_for_display,
                user=user)

    elif request.method == 'GET':
        if actual_question == None:
            return render_template('access-error.html', data_type="answer", id=actual_answer)
        elif actual_answer == None:
            return render_template('access-error.html', data_type="question", id=actual_question)

    elif request.method == 'POST' and 'username' in session and actual_user_id == comment_user_id:
        update_comment = {'id': comment_id,
                          'message': request.form.get('comment'),
                          'submission_time': util.generate_time()}
        data_manager.update_comment(update_comment)
        comment_data = data_manager.get_comment_by_id(comment_id)
        if comment_data[0]['question_id'] is None:
            question_id = data_manager.get_answer_by_id(comment_data[0]['answer_id'])[0]['question_id']
            return redirect(f'/question/{question_id}')
        else:
            comment_data = data_manager.get_comment_by_id(comment_id)
            return redirect(f'/question/{comment_data[0]["question_id"]}')


@app.route('/comments/<comment_id>/delete', methods=['GET'])
def delete_comment(comment_id):
    actual_question = data_manager.get_question_id_by_comment_id(comment_id)
    actual_answer = data_manager.get_answer_id_by_comment_id(comment_id)
    actual_user_id = 'a'

    if 'username' in session:
        actual_user_id = data_manager.get_user_id_by_user_name(session['username'])
    else:
        if actual_question == None:
            return render_template('access-error.html', data_type="answer", id=actual_answer)
        elif actual_answer == None:
            return render_template('access-error.html', data_type="question", id=actual_question)

    comment_user_id = data_manager.get_user_by_comment_id(comment_id)

    if actual_user_id == comment_user_id:
        question_id = request.args.get('question_id')
        data_manager.delete_comment(comment_id)
        return redirect(f'/question/{question_id}')
    else:
        if actual_question == None:
            return render_template('access-error.html', data_type="answer", id=actual_answer)
        elif actual_answer == None:
            return render_template('access-error.html', data_type="question", id=actual_question)


@app.route('/answer/<answer_id>/accept',methods=['GET'])
def accept_answer(answer_id):
    data_manager.accept_answer(answer_id)
    return redirect(f'/answer/{answer_id}')


# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/show-user', methods=['GET', 'POST'])
def show_user():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_password = util.hash_password(request.form['password'])
        data_manager.register_user(request.form['username'], hashed_password, util.generate_time())
        return redirect('/')
    return render_template('register.html', meth='register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        plain_text_password = request.form['password']
        user_name = request.form['username']
        user_hashed_password = data_manager.get_user_password(user_name)
        if user_hashed_password is not None:
            if util.validate_password(plain_text_password, user_hashed_password):
                session['username'] = user_name
        return redirect('/')
    return render_template('register.html', meth='login')


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect('/')


@app.route('/user/<user_id>')
def get_user_profile(user_id):
    if 'username' in session:
        questions = data_manager.get_questions_of_user(int(user_id))
        answers = data_manager.get_answers_of_user(int(user_id))
        comments = data_manager.get_comments_of_user(int(user_id))
        reputation = data_manager.get_reputation_of_user(int(user_id))
        user = data_manager.get_user_by_user_id(int(user_id))
        current_user = util.return_user()
        return render_template('user.html', current_user=current_user, username=user, questions=questions, answers=answers, comments=comments, user=user, reputation=reputation)
    return render_template('access-error.html', data_type='add_new_question')


@app.route('/tags')
def get_all_tags():
    tags = data_manager.get_all_tags()
    return render_template('list-tags.html', tags=tags, user=util.return_user())


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
