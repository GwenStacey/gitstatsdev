from flask import Flask, jsonify, render_template, request
from decouple import config
from dotenv import load_dotenv
from .models import DB, Repo
from .utils import add_or_update_repo, update_all_repos

load_dotenv()


def create_app():
    """Create and configure an instance of the Flask application"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    DB.init_app(app)

    @app.route('/')
    def root():
        return render_template('base.html',
                               title='Home',
                               repos=Repo.query.all())

    @app.route('/repo', methods=['POST'])
    @app.route('/repo/<owner>/<name>', methods=['GET'])
    def repo(owner=None, name=None, message=''):
        owner = owner or request.values['owner']
        name = name or request.values['name']
        try:
            if request.method == 'POST':
                add_or_update_repo(owner, name)
                message = "{} {} successfully added!".format(owner, name)
        except Exception as e:
            message = "Error adding {} {}: {}".format(owner, name, e)

        if request.method == 'GET':
            db_repo = Repo.query.get((owner, name))
            if db_repo:
                message = jsonify(db_repo.as_dict())
            else:
                message = "Repository not found!"

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
