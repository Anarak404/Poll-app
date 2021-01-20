from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SuperSecretKey'
socketio = SocketIO(app, cors_allowed_origins="*")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/votedatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(250))
    answers = db.relationship('Answer', backref='question')


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer_text = db.Column(db.String(150))
    votes = db.Column(db.Integer)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)


@app.route('/', methods=['GET'])
@app.route('/home')
def home():
    return render_template("index.html")


@app.route('/session/<q_id>/', methods=['GET', 'POST'])
def session(q_id):
    title = db.session.query(Question).filter(Question.id == q_id).first_or_404()

    return render_template("session.html", id_question=q_id,
                           question_title=title.question_text,
                           option1=title.answers[0].answer_text,
                           option2=title.answers[1].answer_text,
                           option3=title.answers[2].answer_text)


@app.route('/insert', methods=['POST'])
def insert():
    question = Question(question_text=request.form['q_title'])
    db.session.add(question)
    db.session.commit()

    answers = [
        Answer(answer_text=request.form['a_1'], votes=0, question_id=question.id),
        Answer(answer_text=request.form['a_2'], votes=0, question_id=question.id),
        Answer(answer_text=request.form['a_3'], votes=0, question_id=question.id)
    ]

    db.session.add_all(answers)
    db.session.commit()

    return redirect(url_for('session', q_id=question.id))


@socketio.on('connect')
def connect():
    join_room(request.args['room_id'])


@socketio.on('vote')
def handle_vote(arg):
    ques_id = request.args['room_id']

    question = db.session.query(Question).filter(Question.id == ques_id).first()

    voted_answer_id = question.answers[arg].id

    voted_answer = db.session.query(Answer).filter(Answer.id == voted_answer_id).first()
    new_vote = voted_answer.votes + 1
    voted_answer.votes = new_vote
    db.session.commit()

    result1 = question.answers[0].votes
    result2 = question.answers[1].votes
    result3 = question.answers[2].votes

    emit('vote results', {'result1': result1, 'result2': result2, 'result3': result3}, room=ques_id)


if __name__ == '__main__':
    socketio.run(app, port=8080, debug=True)
