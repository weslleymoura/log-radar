# negocify

### Instalação da stack de dev
Primeiro passo é instalar o **anaconda** na sua máquina.<br>
https://docs.anaconda.com/anaconda/install/linux/

Também será necessário instalar o **postgreSQL**<br>
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-18-04-pt

Em termos de IDE, recomendo **VS Code**<br>
https://code.visualstudio.com/docs/setup/linux

### Configuração do ambiente virtual do python anaconda
A ideia aqui é criar um ambiente python isolado para o projeto, aka *virtual environment*
```
conda create -n negocify-util-env python=3.6
conda activate negocify-util-env
conda install django
pip install python-decouple
pip install psycopg2-binary
pip install Pillow
pip install django-widget-tweaks
pip install stripe
pip install boto3
pip install django-storages
pip install gunicorn
pip install django-heroku
pip install sendgrid
```

### Download do código fonte
Acessar o diretório onde quer salvar o código fonte e clonar o repositório.
```
git clone https://github.com/weslleymoura/negocify.git
```

### Criar um banco de dados local
Precisamos de um banco de dados local que será usado pela aplicação local.
```
sudo -u postgres psql
create role negocifyuser with login password 'password123';
create database negocifydb owner negocifyuser;

Connect to database
\c negocifydb

List tables
\dt
```

### Criando as tabelas no banco de dados
Para criar as tabelas do banco de dados temos que rodar os *migrations*.
```
./manage.py migrate
./manage.py makemigrations
```

Lembrando que sempre que precisar rodar o utilitário ./manage.py, o ambiente virtual do python deve estar ativado
```
conda activate negocify-util-env
```

Se um dia precisar resetar os *migrations*, segue link bastante útil.<br>
https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html

### Criando super user da aplicação
Pra conseguir logar na aplicação também precisamos de um super user.

```
./manage.py createsuperuser
```
Será solicitado nome de usuário e senha

### Iniar aplicação local
```
./manage.py runserver
```

### Fazendo deploy no Heroku
Esses links de referência são muito bons:<br>
https://devcenter.heroku.com/articles/django-app-configuration <br>
https://devcenter.heroku.com/articles/config-vars

Deixei o passo a passo aqui para referência, mas em teoria já está tudo certo.<br>
Pra fazer deploy tem que rodar ```heroku login``` e depois a parte de **push code** que está no final desse documento.

#### Install heroku cli
https://devcenter.heroku.com/articles/heroku-cli
```
sudo snap install --classic heroku
```

#### Create requirements file
```
conda activate negocify-util-env
cd ~/workspace/negocify (your project dir)
pip list --format=freeze > requirements.txt
```

#### Create Procfile
```
touch Procfile
vim Procfile
```
Add the following text:
**web: gunicorn negocify.wsgi --log-file -**

#### Login
```
heroku login
```

#### Create app
```
git init
heroku create negocify
heroku git:remote -a negocify
```
https://negocify.herokuapp.com/ | https://git.heroku.com/negocify.git

#### Create database addon
```
heroku addons:create heroku-postgresql:hobby-dev --app negocify
```

#### Env vars

Variáveis gerais
```
heroku config:set SECRET_KEY=my-secret-key --app negocify
heroku config:set DB_NAME=negocifydb --app negocify
heroku config:set DB_USER=negocifyuser --app negocify
heroku config:set DB_PASSWORD=password123 --app negocify
heroku config:set DB_HOST=localhost --app negocify
heroku config:set DB_PORT=5432 --app negocify
heroku config:set SENDGRID_API_KEY=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 --app negocify
heroku config:set SMTP_PASSWORD_HOST=qheitsazdzevjnqg --app negocify
heroku config:set TELEGRAM_BOT_TOKEN=2124123935:AAHUsDZNrHFFkQ_7LsEooTzMV4XwnnyABn8 --app negocify
```

Variáveis do ambiente de teste
```
heroku config:set NEGOCIFY_ENV=TEST --app negocify
heroku config:set MELHOR_ENVIO_CLIENT_ID=1981 --app negocify
heroku config:set MELHOR_ENVIO_CLIENT_SECRET=SuHkthhHdl3gfcA7oL0fn5kDIiuE4UNh25Cg7HCX --app negocify
heroku config:set MELHOR_ENVIO_CALLBACK=http://localhost:8000/deal/deal/callback-freight-provider/ --app negocify
heroku config:set AWS_STORAGE_BUCKET_NAME=negocify-bucket-test --app negocify
heroku config:set AWS_ACCESS_KEY_ID=AKIA2JSIS32MXTMMKLOB --app negocify
heroku config:set AWS_SECRET_ACCESS_KEY=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 --app negocify
heroku config:set URL_MELHOR_ENVIO=https://sandbox.melhorenvio.com.br --app negocify
heroku config:set PAGARME_PRIVATE_KEY=sk_test_vE6n8q2u4tklzA3R --app negocify
heroku config:set PAGARME_RECIPIENT_ID=rp_5Pv3lPouNuJ4Q8Zd --app negocify
```

Variáveis do ambiente de produção
```
heroku config:set NEGOCIFY_ENV=PROD --app negocify
heroku config:set MELHOR_ENVIO_CLIENT_ID=5785 --app negocify
heroku config:set MELHOR_ENVIO_CLIENT_SECRET=GY9cC2aV5pU7a98GN2i9zRYVMwnagZovcmmZsWTE --app negocify
heroku config:set MELHOR_ENVIO_CALLBACK=https://www.negocify.app/deal/deal/callback-freight-provider/ --app negocify
heroku config:set AWS_STORAGE_BUCKET_NAME=negocify-bucket-prod --app negocify
heroku config:set AWS_ACCESS_KEY_ID=AKIA2JSIS32MXTMMKLOB --app negocify
heroku config:set AWS_SECRET_ACCESS_KEY=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 --app negocify
heroku config:set URL_MELHOR_ENVIO=https://melhorenvio.com.br --app negocify
heroku config:set DEBUG=False --app negocify
heroku config:set PAGARME_PRIVATE_KEY=sk_2q7YLDVh9gfj0VJj --app negocify
heroku config:set PAGARME_RECIPIENT_ID=rp_5M1VkxpiNi6k9nRZ --app negocify
```


#### Push code
Esse link de referência me ajudou. <br>
https://devcenter.heroku.com/articles/git#prerequisites-install-git-and-the-heroku-cli

```
git init
heroku git:remote -a negocify OU negocify-test
```

```
git add .
git commit -m "you message"
git push heroku master
```

#### Migrations
```
heroku run python manage.py migrate --app negocify
heroku run python manage.py createsuperuser --app negocify
```

Reset database
```
heroku pg:reset DATABASE
```

### Dicas sobre django
Quando criei a aplicação pela primeira vez, tive que usar os comandos abaixo.
```
cd workspace/negocify/
mkdir apps
cd apps
../manage.py startapp core
```

### Dicas sobre resolução de conflitos de migrate
É possível acessar o banco de dados pelo comando
```
heroku pg:psql
```

Ao conectar no banco de dados, podemos rodar inserts para resolver problemas de migrations. Exempli:
```
insert into public.django_migrations (app, name, applied) values ('deal', '0018_auto_20211122_1644', '2021-12-11 11:50:00.969441+00');
insert into public.django_migrations (app, name, applied) values ('auth', '0013_auto_20220101_2055', '2022-01-01 11:50:00.969441+00');
```

Para mostrar as migrations executadas
(https://docs.djangoproject.com/en/4.0/topics/migrations/)
```
python manage.py showmigrations auth
```

Fake migrations
```
python manage.py migrate --fake
```

Migrate specific app
```
python manage.py migrate deal
```