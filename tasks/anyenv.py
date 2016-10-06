# -*- coding: UTF-8 -*-

from fabric.api import run, sudo, put, settings

u"""言語install
    * anyenvをinstallし、と其処から以下の言語をinstallする。
        * pyenv(python3, python2)
        * rbenv
        * ndenv(v0.10, 4.4)
        * jenv(java8, maven)

    ※ envの要求
    working_user : user name
    working_pwd  : password
    ssh_port     : ssh login port
"""
def install(env):
    with settings(user=env.working_user, password=env.working_pwd, port=env.ssh_port):
        install_anyenv()
        install_pyenv()
        install_rbenv()
        install_ndenv()
        install_jenv()

# install anyenv
def install_anyenv():
    sudo("rm -rf /usr/local/.anyenv /etc/profile.d/anyyenv.sh")
    sudo("git clone https://github.com/riywo/anyenv /usr/local/.anyenv")
    # ~/ と違うpathでは、ANYENV_ROOTの設定が必要
    sudo("echo 'export ANYENV_ROOT=/usr/local/.anyenv/' >> /etc/profile.d/anyyenv.sh")
    sudo("echo 'export PATH=\"/usr/local/.anyenv/bin:$PATH\"' >> /etc/profile.d/anyyenv.sh")
    sudo("echo 'eval \"$(anyenv init -)\"' >> /etc/profile.d/anyyenv.sh")
    sudo("sh /etc/profile.d/anyyenv.sh")

# install pyenv
def install_pyenv():
    sudo("yum -y install gcc gcc-c++ make git openssl-devel　bzip2-devel zlib-devel readline-devel sqlite-devel bzip2 sqlite openssl-devel")
    sudo("anyenv install pyenv")
    sudo("sh /etc/profile.d/anyyenv.sh")
    sudo("git clone https://github.com/yyuu/pyenv-pip-rehash.git /usr/local/.anyenv/envs/.pyenv/plugins/pyenv-pip-rehash")
    # python3, python2の最新版をinstall
    sudo("pyenv install $(pyenv install -l | grep -v - | tr -d ' ' | grep '^2' | tail -1)")
    sudo("pyenv install $(pyenv install -l | grep -v - | tr -d ' ' | grep '^3' | tail -1)")
    run("pyenv local $(pyenv install -l | grep -v - | tr -d ' ' | grep '^2' | tail -1)")

# install rbenv
def install_rbenv():
    sudo("anyenv install rbenv")
    sudo("sh /etc/profile.d/anyyenv.sh")
    #  安定版 http://mawatari.jp/archives/install-latest-stable-version-of-ruby-using-rbenv
    sudo("rbenv install $(rbenv install -l | grep -v - | tail -1)")
    run("rbenv local $(rbenv install -l | grep -v - | tail -1)")

# install nodebrew
def install_ndenv():
    sudo("anyenv install ndenv")
    sudo("sh /etc/profile.d/anyyenv.sh")
    sudo("ndenv install v0.10.26") # 安定版
    sudo("ndenv install 4.4.6")
    run("ndenv local 4.4.6")
    # npm installによるcommandへのPATHを通す。
    # sudo("echo 'export PATH=\$PATH:`npm bin -g`' >> /etc/profile.d/anyyenv.sh")

# install jenv
def install_jenv():
    sudo("rm -rf /etc/profile.d/maven.sh /usr/local/*")
    sudo("anyenv install jenv")
    sudo("sh /etc/profile.d/anyyenv.sh")
    sudo("wget --no-cookies --no-check-certificate --header \"Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com%2F; oraclelicense=accept-securebackup-cookie\" http://download.oracle.com/otn-pub/java/jdk/8u101-b13/jdk-8u101-linux-x64.rpm -P /usr/local/")
    sudo("yum localinstall -y /usr/local/jdk-8u101-linux-x64.rpm")
    sudo("readlink $(readlink $(which java)) | sed -e 's/jre\\/bin\\/java//' | xargs jenv add")
    sudo("jenv enable-plugin export") # $JAVA_HOMEの切り替えplugin
    sudo("jenv global 1.8")
    # maven install
    sudo("wget http://ftp.riken.jp/net/apache/maven/maven-3/3.3.9/binaries/apache-maven-3.3.9-bin.tar.gz -P /usr/local/")
    sudo("mkdir /usr/local/apache-maven && tar xfvz /usr/local/apache-maven-3.3.9-bin.tar.gz --strip-components=1 -C /usr/local/apache-maven")
    sudo("echo 'export M3_HOME=/usr/local/apache-maven' >>  /etc/profile.d/maven.sh")
    sudo("echo 'M3=$M3_HOME/bin' >>  /etc/profile.d/maven.sh")
    sudo("echo 'export PATH=$M3:$PATH' >>  /etc/profile.d/maven.sh")
