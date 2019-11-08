from flask import Flask,render_template,url_for,request,redirect
from flask_restful import Resource,Api,reqparse
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import sqlite3
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
api = Api(app)


class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200), nullable = False )
    completed = db.Column(db.Integer, default = 0)
    date_created = db.Column(db.DateTime, default = datetime.utcnow )

    def __repr__(self):
        return '<Task %r' %self.id
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form["content"]
        new_task = ToDo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return "there was an issue."
    else:
        tasks = ToDo.query.order_by(ToDo.date_created).all()
        return render_template('index.html',tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = ToDo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "there was an issue deleting this task"

@app.route('/update/<int:id>', methods = ['GET','POST'])
def update(id):
    task = ToDo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "there was an error while updating this task"
    else:
        return render_template('update.html',task=task)

class postAPI(Resource):
    def get(self):
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        data = c.execute("select * from to_do")
        c.close
        return data.fetchall()
    def post(self):
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        parser = reqparse.RequestParser()
        parser.add_argument('task')
        args = parser.parse_args()
        c.execute("""INSERT INTO to_do ('content','completed','date_created') VALUES((?),(?),(?))""",[args['task'],0,datetime.now()])
        conn.commit()
        
api.add_resource(postAPI,'/to_do')

class idAPI(Resource):
    def delete(self,id):
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute("""Delete from to_do where id = {};""".format(id))
        conn.commit()
    def get(self,id):
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        data = c.execute("""Select * from to_do where id = {};""".format(id))
        conn.commit()
        return data.fetchall()
    def put(self,id):
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        parser = reqparse.RequestParser()
        parser.add_argument('task')
        args = parser.parse_args()
        print(args['task'])
        c.execute("""UPDATE to_do SET content = '{0}' where id = {1};
        """.format(args['task'],id))
        conn.commit()
        # c.execute("""UPDATE to_do SET content = {} where\
        # id = {}""".format(args['task'],id))
api.add_resource(idAPI,'/to_do/<int:id>')

if __name__ == "__main__":
    app.run(debug=True) 