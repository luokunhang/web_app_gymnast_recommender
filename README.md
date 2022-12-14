# MSiA423 Template Repository

# Table of Contents
* [Directory structure ](#Directory-structure)
* [Running the app ](#Running-the-app)
	* [1. Initialize the database ](#1.-Initialize-the-database)
	* [2. Configure Flask app ](#2.-Configure-Flask-app)
	* [3. Run the Flask app ](#3.-Run-the-Flask-app)
* [Testing](#Testing)

## Project Charter
##### Vision
In gymnastics, athletes compete over 4 events, each of which contributes to their final score. 
However, each gymnast has stronger and weaker events. 

In the team all around competitions, for each event, all team members do not need to compete, 
so the coach aims to pick a team of gymnasts with different strength for the highest total scores possible. 

In another scenario, if any gymnast had injuries before the competition, an alternate needs to replace 
the injured. Usually, the alternate is desired to have the same strong events, so she could 
compete at the same events.

Let's picture two situations related to the scenarios above:
1. Gymnast X is in the team. Who should we pick as her teammates?
2. Gymnast Y is injured. Who should replace her?

##### Mission
Given a gymnast, an app that clusters gymnasts based on their competition results can generate 
a similar gymnast from the same cluster, or a different gymnast from other clusters.

The data are from the all around final results at the Tokyo Olympic Games from Wikipedia.\
https://en.wikipedia.org/wiki/Gymnastics_at_the_2020_Summer_Olympics_%E2%80%93_Women%27s_artistic_individual_all-around

##### Success Criteria
The primary metric for the unsupervised clustering model is the pseudo F-score. 
Also, the pseudo R-squared should be at least 0.5.

Because the site is for coaches and fans, 
and the business goal is to help professional find better strategies and entertain the fans, 
the number of visits and the probability of revisiting the application should be measured to 
determine the traffic and health of the application.


## Directory structure 

```
├── README.md                         <- You are here
├── api
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs│    
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│   ├── config.yaml                   <- Configurations for codes and functions 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│   ├── Gymmatch.pdf                  <- Slide deck for presentation 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project.
|
├── dockerfiles/                      <- Directory for all project-related Dockerfiles 
│   ├── Dockerfile.app                <- Dockerfile for building image to run web app
│   ├── Dockerfile                    <- Dockerfile for building image to execute run.py  
│   ├── Dockerfile.pipeline           <- Dockerfile for building image to run the ml pipeline
│   ├── Dockerfile.test               <- Dockerfile for building image to run unit tests
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project. No executable Python files should live in this folder.  
│   ├── acquire_data.py               <- Data acquisition
│   ├── clustering.py                 <- Functions in the model training step
│   ├── populate_database.py          <- Database creation and ingestion 
│   ├── app_helper.py                 <- Helper funcs for the flask app
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│   ├── test_clustering.py            <- Unit tests for funcs in clustering.py 
│
├── app.py                            <- Flask wrapper for running the web app 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
├── pipeline.sh                       <- Bash script file for the ml pipeline 
```

## Running the app 
### 1. Prepare the model and data
In this section, commands are provided to pre-compute entities needed for the web app to run.
Model object and data will be saved at designated folder on AWS S3 bucket and RDS database 
(or the local sqlite database).

For the docker run commands in this section, your environment variables must 
be present and correct. The bucket name is required,
and make sure it works with your access key and secret key.
##### Build the image 

To build the image, run from this directory (the root of the repo):
```bash
 docker build -f dockerfiles/Dockerfile -t final-project .
```

The building structure:
1. acquire
2. load_clean
3. features
4. train
5. score
6. evaluate
7. create_database
8. populate_database

You can run the container the whole pipeline or step by step.
#### Approach 1 (recommended): run the pipeline
(steps 2-8) To save the model and files to an s3 bucket run:
```bash
docker build -f dockerfiles/Dockerfile.pipeline -t final-project-pipeline .
docker run -e SQLALCHEMY_DATABASE_URI -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY --mount type=bind,source="$(pwd)"/data,target=/app/data/ final-project-pipeline --s3_bucket_name <your-bucket>
```

#### Approach 2: run a single step
To run each step, use one of the following command:
```bash
docker run -e SQLALCHEMY_DATABASE_URI -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY --mount type=bind,source="$(pwd)"/data,target=/app/data/ final-project <action> --s3_bucket_name <your-bucket>
```
`action` can be one of `acquire`, `load_clean`, `features`, 
`train`, `score`, `evaluate`, `create_database`, `populate_database`.
`your-bucket` should be your own s3 bucket name. If this optional
argument is absent, the default bucket will be used.


#### Notes
Defining your engine string:\
A SQLAlchemy database connection is defined by a string with the following format:

`dialect+driver://username:password@host:port/database`

The `+dialect` is optional and if not provided, a default is used. For a more detailed description of what `dialect` and `driver` are and how a connection is made, you can see the documentation [here](https://docs.sqlalchemy.org/en/13/core/engines.html). We will cover SQLAlchemy and connection strings in the SQLAlchemy lab session on 
##### Local SQLite database 

A local SQLite database can be created for development and local testing. It does not require a username or password and replaces the host and port with the path to the database file: 

```python
engine_string='sqlite:///data/gymnastics.db'

```


### 2. Configure Flask app 

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
import os

DEBUG = True # Keep True for debugging, change to False when moving to production 
LOGGING_CONFIG = "config/logging/local.conf" # Path to file that configures Python logger
PORT = 5000 # What port to expose app on. Must be the same as the port exposed in dockerfiles/Dockerfile.app
APP_NAME = "gym_match"
SQLALCHEMY_TRACK_MODIFICATIONS = True
HOST = '0.0.0.0' # the host that is running the app. 0.0.0.0 when running locally
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 5 # Limits the number of rows returned from the database 

SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
if not SQLALCHEMY_DATABASE_URI:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/gymnastics.db'
```

### 3. Run the Flask app
#### Build the image 

To build the image, run from this directory (the root of the repo): 

```bash
 docker build -f dockerfiles/Dockerfile.app -t final-project-app .
```

This command builds the Docker image, with the tag `gymmatch_app`, 
based on the instructions in `dockerfiles/Dockerfile.app` 
and the files existing in this directory.

#### Running the app

To run the Flask app, run:
```bash
docker run --name gymmatch_apptest -e SQLALCHEMY_DATABASE_URI -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY --mount type=bind,source="$(pwd)"/data,target=/app/data/ -it -p 0.0.0.0:5001:5000 final-project-app
```
You should be able to access the app at http://127.0.0.1:5001/ in your browser (Mac/Linux should also be able to access the app at http://0.0.0.0:5001/ or localhost:5000/) .

The arguments in the above command do the following: 

* The `--name gymmatch_apptest` argument names the container "test". This name can be used to kill the container once finished with it.
* The `--mount` argument allows the app to access your local `data/` folder so it can read from the SQLlite database created in the prior section. 
* The `-p 5001:5000` argument maps your computer's local port 5000 to the Docker container's port 5000 so that you can view the app in your browser. If your port 5000 is already being used for someone, you can use `-p 5001:5000` (or another value in place of 5001) which maps the Docker container's port 5000 to your local port 5001.

Note: If `PORT` in `config/flaskconfig.py` is changed, this port should be changed accordingly (as should the `EXPOSE 5000` line in `dockerfiles/Dockerfile.app`)


#### Kill the container 

Once finished with the app, you will need to kill the container. If you named the container, you can execute the following: 

```bash
docker kill gymmatch_apptest
```
where `gymmatch_apptest` is the name given in the `docker run` command.

If you did not name the container, you can look up its name by running the following:

```bash 
docker container ls
```

The name will be provided in the right most column. 

## Testing

Run the following:

```bash
 docker build -f dockerfiles/Dockerfile.test -t final-project-test .
```

To run the tests, run: 

```bash
 docker run final-project-test
```

The following command will be executed within the container to run the provided unit tests under `tests/`:  

```bash
python -m pytest
```
