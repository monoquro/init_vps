# -*- coding: UTF-8 -*-

from fabric.api import run, sudo, put, settings

u"""nginx install
    * nginxをinstallし、/home/${user}/public_htmlからhtmlを公開する。
        * 実行するとpublic_htmlは消され、再度作られる。

    ※ envの要求
    ip           : vps's ip address
    working_user : user name
    working_pwd  : password
    ssh_port     : ssh login port
"""
def install(env):
    with settings(user=env.working_user, password=env.working_pwd, port=env.ssh_port, warn_only=True):
      sudo("rm /etc/nginx/conf.d/custom.conf")
      run("rm -rf ~/public_html")
      sudo('yum install -y nginx')
      sudo('service nginx start', pty=False)
      sudo("chkconfig nginx on")
      sudo('echo "server {" >> /etc/nginx/conf.d/custom.conf')
      sudo('echo "    listen 80;" >> /etc/nginx/conf.d/custom.conf')
      sudo('echo "    server_name %s;" >> /etc/nginx/conf.d/custom.conf' % (env.ip))
      sudo('echo "    location ~ ^/~(.+?)(/.*)?$ {" >> /etc/nginx/conf.d/custom.conf')
      sudo('echo "        alias /home/\\\$1/public_html\\\$2;" >> /etc/nginx/conf.d/custom.conf')
      sudo('echo "        index  index.html index.htm;" >> /etc/nginx/conf.d/custom.conf')
      sudo('echo "        autoindex on;" >> /etc/nginx/conf.d/custom.conf')
      sudo('echo "    }" >> /etc/nginx/conf.d/custom.conf')
      sudo('echo "}" >> /etc/nginx/conf.d/custom.conf')
      sudo("chmod 711 /home/%s" % (env.working_user))
      run("mkdir ~/public_html")
      sudo("chmod 755 /home/%s/public_html" % (env.working_user))
      run('echo "hello world by %s" >> ~/public_html/index.html' % (env.working_user))
      sudo('service nginx restart', pty=False)
