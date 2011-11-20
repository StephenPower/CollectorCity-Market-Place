
## Commands to install the project

Some linux variants will run into problems in the buildout process.
Make sure the following packages are installed on your system:
apache2 apache2-devel mysql mysql-devel gcc swig python-devel python-setuptools
Some systems may have different package names or require additional packages.

Set up apache with the following VirtualHost example:
<VirtualHost *:80>
	ServerAdmin user@localhost
	DocumentRoot /opt/CollectorCity-Market-Place
	ServerName mydomain.com
	ServerAlias www.mydomain.com
	ErrorLog /var/log/apache2/CollectorCity-Market-Place-error.log
	CustomLog /var/log/apache2/CollectorCity-Market-Place-access.log combined
	Alias /media/admin /opt/CollectorCity-Market-Place/auctions-env/lib/python2.6/site-packages/django/contrib/admin/media
	Alias /media /opt/CollectorCity-Market-Place/marketplaces/media
	Alias /favicon.ico /opt/CollectorCity-Market-Place/marketplaces/media/favicon.ico
	Alias /robots.txt /opt/CollectorCity-Market-Place/marketplaces/media/robots.txt

	<Directory /opt/CollectorCity-Market-Place/media>
		Order deny,allow
		Allow from all
	</Directory>

	WSGIDaemonProcess user processes=1 threads=2 python-path=/opt/CollectorCity-Market-Place/auctions-env/lib/python2.6/site-packages user=user group=user
	WSGIProcessGroup user
	WSGIScriptAlias / /opt/CollectorCity-Market-Place/deploy/marketplaces.wsgi

	<Directory /opt/CollectorCity-Market-Place>
		Order deny,allow
		Allow from all
	</Directory>
</VirtualHost>



virtualenv --no-site-packages --python=python2.6 auctions-env

pip -E auctions-env install --requirement=auctions/deploy/requirements.txt

source auctions-env/bin/activate

The Deploy Directory should contain djangoflash.zip and the gchecky.zip files
The libs directory should contain the geopy, pickefield, pyExcelerator, reversion, south and storages directories

See requirements.txt for more info

cd /CollectorCity-Market-Place/
chmod +x manage.py
# crear db en mysql, editar settings.py 
./manage.py syncdb
./manage.py runserver


### Crons ###
1) cron_week_topsellert.py 
To get the best seller of the week. run once a week (could be all mondays) 

2) cron_send_daily_invoice
Daily invoices. Cron that sends the invoices to customers... Should be run once a day, every day...

3) cron_past_due.py
Should be run every day, once a day. It checks which customer do not paid their subscription, send mail to site admins..


### RUN SOLR
java -Dsolr.solr.home=multicore -server -jar start.jar

4) Reindex sorl objects
python manage.py update_index -a 1
## Commands to install the project
easy_install virtualenv pip
virtualenv --no-site-packages --python=python2.6 auctions-env
pip -E auctions-env install --requirement=deploy/requirements.txt
source auctions-env/bin/activate
cd marketplaces
chmod +x manage.py
# edit settings.py set DEBUG=True to so runserver serves media files.
# edit settings.py to set database info (use sqlite3 for non-production)
./manage.py syncdb
./manage.py migrate

