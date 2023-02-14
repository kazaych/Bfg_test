
## Описание запуска стенда
<br>

1. Для запуск стенда необходимы следующие компоненты, установленные на хостовой машине: 
 - Virtualbox
 - Ansible
 - Vagrant

 2. Пулим репо, заходим в папку с проектом и запускаем стенд командой start.sh. Ansible playbook для конфигурайии виртуальной машины запустится в автомате. По умолчанию для гостевой машины установлены следующие параметры по использованию ресурсов хоста:
 - Количество цп: 2
 - ОЗУ: 2048 мб  

<br>

## Описание файлов стенда.
<br>

 1. В файле defaults/main.yml описаны основные переменные, влияющие на работу стенда:
 - test_app: true - запускать ли тестовое приложение с unicorn для демонстрации работы связки nginx + gunicorn + python app, этот парметр так же будет влият на то на какой порт будет проксить nginx: при true на 8080, при false на 8081;
- python_from_source: true - если необходимо компилировать питон из исходников, то необходимо ставить в true;
- python_source_url: https://www.python.org/ftp/python/3.6.13/Python-3.6.13.tgz - ссылка на архив с исходником;
- python_version_name: Python-3.6.13 - имя папки в которой будем подготавливать
исходник. Имя пакета без расширения;
- python_dir: /home/bfg/.python - папка куда установится питон;

- db_user: root - имя пользователя БД;
- db_password: 12345 - пароль;
- db_name: stack_exchange - имя базы данных;

2. В папке /templates лежат шаблоны следующих конфигов:

- gunicorn_stack.service.j2 - systemd unit для запуска gunicorn для stack_over_search как сервиса;
- gunicorn_tst.service.j2 - юнит для тестового приложения; 
- nginx.conf.j2 - конфиг nginx;
- root_cnf.j2 - конфиг для подключения к базе по ssh;
- settings.ini.j2 - конфиг stack_oversearch

3. В корне находятся следующие файлы:

- Hosts.yml - inventory для плейбука;
- ansible.cfg - файл настройки ansible;
- playbook.yml - основной плейбук


<br>

## Описание работы стенда.
<br>

1. После запуска создаем пользователя и группу bfg, забираем приложение из гита, устанавливаем зависимости.
2. Запускаем MySQL и Redis как сервисы, копируем конфиг ngninx из шаблона.
3. Далле запускаем таски по сбору питона из исходников( папки и версию указываются через переменные)- будут собраны только в том случае, если переменная python_from_source: true.
4. Далее конфигурим базу данных: 
- Апдейтим пароль и привилегии для пользователя root;
- Создаем базу данных;
- Ресторим таблицы из tables.sql;
- Сохраняем конфиг для подключения к БД по ssh;
5. Создаем кружение для приложения stack_over_search:
- создаем папки для конфигов и логов;
- закидываем конфиг из шаблона;
- создаем виртуальное окружение с помощью скомпилированного python.
- копиуем конфиг systemd unit для gunicorn из шаблона.
- запускаем systemd gunicorn для приложения с 5 воркерами c помощью handlers.
6. Все операции, указанные выше повторяем для тестового приложения.
---
**Обратите внимание!!! В связи с компиляцией питона из исходников - конфигурация может занять сущственное время- наберитесь терпения!!! Примерное время запуска 40 мин, при отключении сборки из исходников около 5-10- зависит от ресурсов виртуальной машны.**

<br>

# Проверка.

1. Запустим стенд без сборки из исходников, зайдем на виртуальную машину и проверим, что тестовое приложение работает через nginx и gunicorn c 4 worker'ами.
```console
vagrant@server:~$ curl localhost
Welcome home!vagrant@server:~$ 

● nginx.service - A high performance web server and a reverse proxy server
   Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
   Active: active (running) since Thu 2023-01-19 16:44:47 UTC; 13min ago

sudo systemctl status gunicorn_tst.service 
● gunicorn_tst.service - Test app gunicorn daemon
   Loaded: loaded (/etc/systemd/system/gunicorn_tst.service; enabled; vendor preset: enabled)
   Active: active (running) since Thu 2023-01-19 16:44:50 UTC; 13min ago
 Main PID: 11250 (gunicorn)
    Tasks: 5 (limit: 2360)
   CGroup: /system.slice/gunicorn_tst.service
           ├─11250 /home/vagrant/tst/venv/bin/python3.6 /home/vagrant/tst/venv/bin/gunicorn my_app_module:my_web_app --bind
           ├─11306 /home/vagrant/tst/venv/bin/python3.6 /home/vagrant/tst/venv/bin/gunicorn my_app_module:my_web_app --bind
           ├─11309 /home/vagrant/tst/venv/bin/python3.6 /home/vagrant/tst/venv/bin/gunicorn my_app_module:my_web_app --bind
           ├─11311 /home/vagrant/tst/venv/bin/python3.6 /home/vagrant/tst/venv/bin/gunicorn my_app_module:my_web_app --bind
           └─11312 /home/vagrant/tst/venv/bin/python3.6 /home/vagrant/tst/venv/bin/gunicorn my_app_module:my_web_app --bind

```
2. Проверим, что MySQL и REDIS подняты, в базе есть нужные таблицы.

```console
mysql> SHOW TABLES;
+--------------------------+
| Tables_in_stack_exchange |
+--------------------------+
| requests                 |
| requests_data            |
+--------------------------+
2 rows in set (0.00 sec)

● redis-server.service - Advanced key-value store
   Loaded: loaded (/lib/systemd/system/redis-server.service; enabled; vendor preset: enabled)
   Active: active (running) since Thu 2023-01-19 16:41:37 UTC; 38min ago
     Docs: http://redis.io/documentation,
           man:redis-server(1)
 Main PID: 4700 (redis-server)
    Tasks: 4 (limit: 2360)
   CGroup: /system.slice/redis-server.service
           └─4700 /usr/bin/redis-server 127.0.0.1:6379

vagrant@server:~$ ss -tulnp |grep 6379
tcp   LISTEN  0        128                127.0.0.1:6379          0.0.0.0:*                                                                                     
tcp   LISTEN  0        128                    [::1]:6379             [::]:*      

```
3. Проверим, что пользователь bfg создан и в его каталоге есть приложение и виртуальное окружение.

```console
vagrant@server:/home/bfg/stack_over_search$ pwd
/home/bfg/stack_over_search
vagrant@server:/home/bfg/stack_over_search$ ll
total 36
drwxr-xr-x 5 bfg bfg 4096 Jan 19 16:43 ./
drwxr-xr-x 4 bfg bfg 4096 Jan 19 16:42 ../
drwxr-xr-x 8 bfg bfg 4096 Jan 19 16:37 .git/
-rw-r--r-- 1 bfg bfg 2642 Jan 19 16:37 README.md
-rw-r--r-- 1 bfg bfg  126 Jan 19 16:37 requirements.txt
-rw-r--r-- 1 bfg bfg  942 Jan 19 16:37 setup.py
drwxr-xr-x 4 bfg bfg 4096 Jan 19 16:37 stackoversearch/
-rw-r--r-- 1 bfg bfg  747 Jan 19 16:37 tables.sql
drwxr-xr-x 6 bfg bfg 4096 Jan 19 16:43 virtualenv/

```

4. Так как nginx и redis запущены как сервисы systemd их сообщения пишутся в /var/log/messages и в свои папки логов по умолчанию /var/log/nginx, /var/log/redis

5. P.S: пароль для юзера bfg - 123.
