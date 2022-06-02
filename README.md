# log-radar
This page explains how to setup a local environment to develop and test loaf-radar, as well general instructions to reproduce it's deployment to heroku.
Some commands are available in this page only for mac users. If you are using another operating system, please convert the commands accordinly.

### Git clone
Let's start by cloning the project repo.
```git clone git@github.com:weslleymoura/log-radar.git```

Of course, if your public ssh key was not added to the project repo (by an admin), you should clone via http.
```https://github.com/weslleymoura/log-radar.git```

### Dev stack instalation
The easiest way to configure the development environment on your machine is installing **anaconda** on your localhost.<br>
https://docs.anaconda.com/anaconda/install/linux/

Additionally, please make sure you have **postgreSQL** installed on your localhost.<br>
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-18-04-pt

In terms of IDE, I recommend **VS Code**<br>
https://code.visualstudio.com/docs/setup/linux

Finally, you can also install **docker** just to test the image we will be deploying to heroku<br>
```brew cask install docker```

### Configuração do ambiente virtual do python anaconda
Make sure you are in the root directory of the project. Let´s create a python environment to isolate the application.

```
conda create -n log-radar--util-env python=3.6
conda activate log-radar-util-env
pip install -r requirements.txt
```

### Creating a local database
Let's create a local database which will be connected to log-radar

```
psql
create role kafkauser with login password 'kafkapass';
create database kafkadb owner kafkauser;

Connect to database
\c kafkadb

List tables
\dt
```

### Running database migrations
Make sure you are in the *root directory* of the project AND your *python virtual environment is activated*.

```
./manage.py migrate
./manage.py makemigrations
```

In case you want to reset migrations, please refer to the following link.<br>
https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html

### Creating a super user in the application
We will create an admin user into the application.

```
./manage.py createsuperuser
```

Type the username and password, as requested.

### Starting up log-radar i the localhost
```
./manage.py runserver
```

Note: you can also run your application on docker containers. This is specially interesting to test your deployment image.
In cse you want to explore it a little more, please refer to https://testdriven.io/blog/deploying-django-to-heroku-with-docker/

### Deploying log-radar on Heroku
Along with the traditional Git plus slug compiler deployments (git push heroku master), Heroku also supports Docker-based deployments, with the Heroku Container Runtime. We will be doing a container-based deployment.

**Note:** if you have already created your application and you just want to **redeploy your code**, all you have to do is jumping to sub-section **Push code**

#### Install heroku CLI

Installing heroku CLI is needed to interact with your heroku account.

```
sudo snap install --classic heroku
```

More information at https://devcenter.heroku.com/articles/heroku-cli

#### Creating a specific directory only for deployment purposes
Based on my experience, it is worth to create a new directory, outside the root directory where you have clone the git repo, which will be used only for deployment purposes.
This is specially helpful because heroku also needs a git repo to make deployments, so you will not mess up the *project git repo* and the *heroku git repo*.

That being said, just copy and past all files** from your project git repo directory to the new deployment directory.

**all fies: DO NOT copy the folder .git 

#### Login
Access your new deployment dirextory and run.

```
heroku login
```

#### Create app

Here, I am creating a heroku app named log-radar. Of course, you would have to specify another name for your own deployment.
```
heroku create log-radar
```
https://log-radar.herokuapp.com/ | https://git.heroku.com/log-radar.git

#### Adjusting settings.py according to your application name
Go to ```settings.py``` and change ```log-radar``` by the name of your application.

```ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'log-radar.herokuapp.com']```

#### Pointing your deployment directory to heroky git account
```
git init
heroku git:remote -a log-radar
```

#### Create database addon
Here we are creating our application database. Please, change ```--app log-radar``` to your application name.

```
heroku addons:create heroku-postgresql:hobby-dev --app log-radar
```

#### Env vars
Let´s now set some environment variables. Please, change ```--app log-radar``` to your application name.

```
heroku config:set DEBUG=False --app log-radar
heroku config:set SECRET_KEY=my-secret-key --app log-radar
heroku config:set AWS_ACCESS_KEY_ID_WM=AKIA6IQSWMH33M4B57NC --app log-radar
heroku config:set AWS_SECRET_ACCESS_KEY_WM=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 --app log-radar
```

#### Setting up heroku stack
We need to advice heroku that we are doing a container-based deployment, build via heroku container registry. Please, change ```--app log-radar``` to your application name.

```heroku stack:set container -a log-radar```

#### Log into heroku container registry

```heroku container:login```

#### Push code
The following commands will trigger your application deployment

```
docker buildx build --load --platform linux/amd64 -t registry.heroku.com/log-radar/web .
docker push registry.heroku.com/log-radar/web
heroku container:release -a log-radar web
```

#### Running migrations
We need to setup the applciation database.
```
heroku run python manage.py migrate --app log-radar
```

And now create a super user to the application, so that you can access the django admin module.
```
heroku run python manage.py createsuperuser --app log-radar
```

### Reference links

Heroku Deployment
1. https://testdriven.io/blog/deploying-django-to-heroku-with-docker/
2. https://devcenter.heroku.com/articles/django-app-configuration
3. https://devcenter.heroku.com/articles/config-vars
4. https://devcenter.heroku.com/articles/git#prerequisites-install-git-and-the-heroku-cli
5. https://stackoverflow.com/questions/66982720/keep-running-into-the-same-deployment-error-exec-format-error-when-pushing-nod

DenStream
1. https://github.com/waylongo/denstream/blob/master/codes/DenStream_clustering.ipynb
2. https://github.com/issamemari/DenStream

Kernel Density Estimation
1. https://jakevdp.github.io/PythonDataScienceHandbook/05.13-kernel-density-estimation.html
2. https://stackoverflow.com/questions/30145957/plotting-2d-kernel-density-estimation-with-python
3. https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gaussian_kde.html
4. https://jakevdp.github.io/blog/2013/12/01/kernel-density-estimation/
5. https://stackoverflow.com/questions/5666056/matplotlib-extracting-data-from-contour-lines
6. https://stackoverflow.com/questions/19418901/get-coordinates-from-the-contour-in-matplotlib
7. https://towardsdatascience.com/generate-contour-plots-using-pythons-matplotlib-1b5a5be804f2
8. https://stackoverflow.com/questions/19311957/plot-contours-for-the-densest-region-of-a-scatter-plot
9. https://stackoverflow.com/questions/31542843/inpolygon-examples-of-matplotlib-path-path-contains-points-method

SNS and SQS
1. https://docs.aws.amazon.com/sns/latest/dg/SendMessageToHttp.prepare.html
2. https://github.com/asaguado/django-amazon-sns
3. https://hands-on.cloud/working-with-sqs-in-python-using-boto3/#h-read-and-delete-messages-from-the-sqs-queue
