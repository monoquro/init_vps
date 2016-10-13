# -*- coding: UTF-8 -*-

from fabric.api import run, sudo, put, settings

u"""cloud9 install
    * cloud9をinstallし、任意のportで公開する。
        * 2度の実行は想定していない。
            * /etc/rc.localに過剰な設定が追加される。

    ※ envの要求
    working_user : user name
    working_pwd  : password
    ssh_port     : ssh login port
    cloud9_port  : cloud9's port
"""
def install(env):
    with settings(user=env.working_user, password=env.working_pwd, port=env.ssh_port):
        port = env.cloud9_port
        user = env.working_user
        pswd = env.working_pwd
        run('rm -rf ~/cloud9 ~/workspace')
        run('npm cache clean')
        run('npm install nak')
        run('mkdir ~/workspace')
        sudo('yum -y install glibc-static') # https://github.com/c9/install/issues/75
        sudo('yum -y install nodejs npm --enablerepo=epel')
        sudo("sed -i 's/LANG=.\+/LANG=\"en_US.UTF-8\"/' /etc/sysconfig/i18n")
        run("git clone git://github.com/c9/core.git ~/cloud9")
        run("sh ~/cloud9/scripts/install-sdk.sh")
        sudo("npm install forever -g")
        sudo("iptables -A INPUT -p tcp -m tcp --dport %s -j ACCEPT" % (port))
        sudo("iptables -L --line-numbers -n")
        sudo("service iptables save")
        sudo("service iptables restart")
        sudo("echo 'su - %s -c \"forever start /home/%s/cloud9/server.js -w /home/%s/workspace -p %s -a %s:%s --listen %s\"' >> /etc/rc.local" % (user, user, user, port, user, pswd, env.ip))
        sudo("chmod u+x /etc/rc.local")
        sudo("sh /etc/rc.local")
