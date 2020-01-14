import connection


@connection.connection_handler
def get_all_questions(cursor, order={'order_by': 'id', 'order_direction': 'asc'}):
    cursor.execute(f"""
    SELECT * FROM question
    ORDER BY {order['order_by']} {order['order_direction'].upper()};
    """)
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def insert_new_question(cursor, title, message, submission_time, view_number, vote_number, image):
    cursor.execute(f"""
    INSERT INTO question
    (title, message, submission_time, view_number, vote_number, image)
    VALUES ('{ title }', '{ message }', '{submission_time}', '{view_number}', '{vote_number}', '{image}')
    """)
    cursor.execute(f"""
    SELECT id FROM question
    WHERE submission_time='{submission_time}';""")
    id = cursor.fetchall()
    print(id[0]['id'])
    return str(id[0]['id'])


@connection.connection_handler
def get_question_by_id(cursor, id):
    cursor.execute(f"""
    SELECT * FROM question
    WHERE id={id}""")
    question = cursor.fetchall()
    return question[0]
