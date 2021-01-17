from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/poll'
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
    print(q_id)
    return "Dziala"


@app.route('/insert', methods=['POST'])
def insert():
    question = Question(question_text=request.form['q_title'])
    db.session.add(question)
    db.session.commit()

    answer1 = Answer(answer_text=request.form['a_1'],
                     votes=0,
                     question_id=question.id)

    answer2 = Answer(answer_text=request.form['a_2'],
                     votes=0,
                     question_id=question.id)

    answer3 = Answer(answer_text=request.form['a_3'],
                     votes=0,
                     question_id=question.id)

    db.session.add(answer1)
    db.session.add(answer2)
    db.session.add(answer3)
    db.session.commit()

    return redirect(url_for('session', q_id=question.id))


if __name__ == '__main__':
    app.run()
