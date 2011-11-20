from __future__ import with_statement

from fabric.api import *
from fabric import state


state.output['debug'] = True

def beta():
    env.hosts = ['www.knewmismatic.com']
    env.user = None
    env.password = None
    env.virtualenv = '/home/beta/ENV'
    env.repository = '/home/beta/poc'
    env.repository_user = 'beta'
    env.user = 'beta'
    #prompt('username: ', 'user')
    #prompt('password: ', 'password')


def update():
    with cd(env.repository):
        run("hg pull -u")
        run("%s/bin/python %s/stores/manage.py migrate" % (env.virtualenv, env.repository))
        run("%s/bin/python %s/marketplaces/manage.py migrate" % (env.virtualenv, env.repository))

def apache_restart():
    sudo("/etc/init.d/apache2 restart")
 
def deploy():
    update()
    apache_restart()
    
    
       
