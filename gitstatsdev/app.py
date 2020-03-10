from flask import Flask, jsonify, render_template, request, Response
from decouple import config
from dotenv import load_dotenv
from .models import DB, Repo
from .utils import add_or_update_repo, update_all_repos, update_pull_requests
import psycopg2
import os

load_dotenv(override=True)
host = os.getenv('RDS_HOSTNAME')
port = os.getenv('RDS_PORT')
db = os.getenv('RDS_DB_NAME')
usern = os.getenv('RDS_USERNAME')
passw = os.getenv('RDS_PASSWORD')

def create_app():
    """Create and configure an instance of the Flask application"""
    app = Flask(__name__)
    #app.config['SQLALCHEMY_DATABASE_URI'] = config('RDS_HOSTNAME')
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #DB.init_app(app)

    @app.route('/')
    def root():
        return render_template('base.html',
                               title='Home',)

    @app.route('/repo', methods=['POST'])
    @app.route('/repo/<owner>/<name>', methods=['GET'])
    def repo(owner=None, name=None, message=''):
        owner = owner or request.values['owner']
        name = name or request.values['name']
        # try:
        if request.method == 'POST':
            return Response(add_or_update_repo(owner, name, app),
                            mimetype='text/html')
        # except Exception as e:
        #    message = "Error adding {} {}: {}".format(owner, name, e)

        if request.method == 'GET':
            db_repo = Repo.query.get((owner, name))
            if db_repo:
                message = jsonify(db_repo.as_dict())
            else:
                message = "Repository not found!"

        return message
    
    @app.route('/updatePRs/<owner>/<name>', methods=['GET'])
    def updating(owner='scikit-learn', name='scitkit-learn', message='Enter an owner and repo name!'):
        owner = owner or request.values['owner']
        name = name or request.values['name']
        conn = psycopg2.connect(database=db, user=usern,
                                password=passw, host=host,
                                port=port)
        update_pull_requests(conn,owner,name)
        message = f'Added all pull requests for Owner {owner} Repo {name}'
        return message

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return 'Reset database!'

    @app.route('/update')
    def update():
        update_all_repos()
        return render_template('base.html',
                               repos=Repo.query.all(),
                               title='All repositories updated!')

    return app
