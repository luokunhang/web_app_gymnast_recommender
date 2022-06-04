import logging.config
import sqlite3
import traceback
import yaml
import argparse

import sqlalchemy.exc
from flask import Flask, render_template, request, redirect, url_for

# For setting up the Flask-SQLAlchemy database session
from src.populate_database import Results, UserInputs, ResultsManager
from src.app_helper import get_label_for_input

# Initialize the Flask application
app = Flask(__name__, template_folder="app/templates",
            static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug(
    'Web app should be viewable at %s:%s if docker run command maps local '
    'port to the same port as configured for the Docker container '
    'in config/flaskconfig.py (e.g. `-p 5001:5000`). Otherwise, go to the '
    'port defined on the left side of the port mapping '
    '(`i.e. -p THISPORT:5000`). If you are running from a Windows machine, '
    'go to 127.0.0.1 instead of 0.0.0.0.', app.config["HOST"]
    , app.config["PORT"])

with open('config/config.yaml', 'r', encoding='utf8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

parser = argparse.ArgumentParser(description="Run the gymnast matching app")
parser.add_argument('--s3_bucket_name',
                    help='Provide your own bucket name or default will be used.',
                    default='2022-msia423-luo-kunhang')
args = parser.parse_args()

result_manager = ResultsManager(app)


@app.route('/')
def index():
    """Main view that lists songs in the database.

    Create view into index page that uses data queried from Track database and
    inserts it into the app/templates/index.html template.

    Returns:
        Rendered html template

    """

    try:
        matchings = result_manager.session.query(UserInputs).all()
        results = result_manager.session.query(Results).all()
        logger.debug("Index page accessed")
        return render_template('index.html',
                               matchings=matchings[-app.config["MAX_ROWS_SHOW"]:],
                               results=results)
    except sqlite3.OperationalError as e:
        logger.error(
            "Error page returned. Not able to query local sqlite database: %s."
            " Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], e)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as e:
        logger.error(
            "Error page returned. Not able to query MySQL database: %s. "
            "Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], e)
        return render_template('error.html')
    except:
        traceback.print_exc()
        logger.error("Not able to display tracks, error page returned")
        return render_template('error.html')


@app.route('/add', methods=['POST'])
def add_entry():
    """View that process a POST with new song input

    Returns:
        redirect to index page
    """

    try:
        user_input = {
            'gymnast': request.form['gymnast'],
            'vault': float(request.form['vault']),
            'uneven_bars': float(request.form['bars']),
            'balance_beam': float(request.form['beam']),
            'floor_exercise': float(request.form['floor'])
        }
        # get label
        label = get_label_for_input(user_input, config, args.s3_bucket_name)
        user_input['label'] = label

        # get similar and different gymnast from RDS
        similar = result_manager.get_matched_gymnast(label, False)
        different = result_manager.get_matched_gymnast(label, True)
        user_input['similar'] = similar.gymnast
        user_input['different'] = different.gymnast

        # write to user_input table
        result_manager.add_user_input(user_input)
        logger.info("New gymnast added: %s", request.form['gymnast'])
        return redirect(url_for('index'))
    except sqlite3.OperationalError as e:
        logger.error(
            "Error page returned. Not able to interact with the sqlite "
            "database: %s. Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], e)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as e:
        logger.error(
            "Error page returned. Not able to interact with the MySQL database: %s. "
            "Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], e)
        return render_template('error.html')
    except Exception as e:
        logger.error(
            "Other error occurred %s .", e
        )
        return render_template('error.html')
    except Exception as e:
        logger.error(
            "Unknown error %s ", e
        )
        return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"],
            host=app.config["HOST"])
