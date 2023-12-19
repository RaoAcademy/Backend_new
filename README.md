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

# Project_X
Test taking platform
With Flask Mysql
with app.app_context(): #for cheapohosting




#mysql db based
SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));


restore db
mysql -u username -ppassword db_name < backupname

#for 1st time start mysql service and hit enter on password for below command, then add create user and etc
sudo mysql -u root -p;
CREATE USER 'tej'@'localhost' IDENTIFIED BY 'tej';
create database project_x;
GRANT ALL PRIVILEGES ON project_x.* TO 'tej'@'localhost';

#requirements
pip3 install flask
pip3 install SQLAlchemy Flask-SQLAlchemy
sudo apt install mysql-server
sudo apt-get install build-essential
pip3 install mysqlclient
pip3 install flask-wtf
pip3 install pandas-ods-reader
pip3 install apscheduler
pip3 install firebase-admin
pip3 install google-auth google-auth-oauthlib google-api-python-client google-api-python-client



#check question completeness
select id from question where format=1 and id not in (select questionId from questionMcqMsqDadSeq);


#for aws code updates
# sudo service gunicorn restart

#vi /var/log/syslog
# zero ssl

sudo vi /etc/nginx/sites-enabled/project_x
server {
    listen 80;
    listen 443 ssl;

    ssl on;
    ssl_certificate /etc/ssl/certs/certificate.crt;
    ssl_certificate_key /etc/ssl/private/private.key;
    server_name 3.109.57.171 raoacademy.com;

    location / {
            proxy_pass http://127.0.0.1:5000;
    }
}

sudo service nginx restart

sudo nano /etc/systemd/system/gunicorn.service
[Unit]
Description:Gunicron service
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/Project_X
ExecStart=/usr/bin/gunicorn --bind 127.0.0.1:5000 --timeout 30 -w 4 -m 007 app:app
Restart=always
RestartSec=5
ExecStop=/home/ubuntu/gunicorn_monitor.sh

[Install]
WantedBy=multi-user.target

sudo service gunicorn restart



main errors while writing error exceptions are-
if frontend wants some data mandatorily - give that.
