# -*- coding: UTF-8 -*-

from fabric.api import run, sudo, put

u"""初期設定
    * env.working_user, env.working_pwdに基づき、userを作成する。
    * security設定をする。
        * ssh loginをenv.ssh_authorized_keysのpub fileに記載されているkeyに制限する。
    
    ※ envの要求
    working_user : user name 
    working_pwd  : password
    ssh_port     : ssh login port
    ssh_authorized_keys : local's pub flie
    root_mail    : your mail address
"""
def server_setup(env):
  add_new_user(env.working_user, env.working_pwd)
  setup_su()
  setup_sudo()
  setup_sshd(env.working_user, env.ssh_port, env.ssh_authorized_keys)
  setup_iptables(env.ssh_port)
  yum_update()
  stop_ipv6()
  stop_service()
  set_root_address(env.root_mail)

def add_new_user(user_name, password):
  run('useradd %s -G wheel' % (user_name) )
  run("echo '%s:%s' | chpasswd" % (user_name, password) )

def setup_su():
  run("sed -i 's/^#auth\(\s\+required\)/auth\\1/' /etc/pam.d/su")

def setup_sudo():
  run("sed -i 's/^# %wheel\(\s\+ALL=(ALL)\s\+ALL$\)/%wheel\\1/' /etc/sudoers")
  # http://qiita.com/akito1986/items/e9ca48cfcd56fdbf4c9d
  run("sed -i 's/^Defaults\s\+secure_path\s\+/#\\0/' /etc/sudoers")

def setup_sshd(user_name, ssh_port, path):
  # SSHのポート番号変更
  run("sed -i 's/^#Port\s\+22/Port %s/' /etc/ssh/sshd_config"  % (ssh_port) )
  # rootのSSHログイン禁止
  run("sed -i 's/^#PermitRootLogin\s\+yes/PermitRootLogin no/' /etc/ssh/sshd_config")
  # 公開鍵認証を有効にする
  run("sed -i 's/^#PubkeyAuthentication\s\+yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config")
  # パスワードログインの禁止
  run("sed -i 's/^PasswordAuthentication\s\+yes/PasswordAuthentication no/' /etc/ssh/sshd_config")
  # SSHを許可するユーザの制限
  run('echo "AllowUsers %s" >> /etc/ssh/sshd_config' % (user_name))
  # サーバに登録する公開鍵の事前準備
  sudo('mkdir /home/%s/.ssh' % (user_name), user=user_name)
  sudo('chmod 700 /home/%s/.ssh' % (user_name), user=user_name)
  sudo('touch /home/%s/.ssh/authorized_keys' % (user_name), user=user_name)
  sudo('chmod 600 /home/%s/.ssh/authorized_keys' % (user_name), user=user_name)
  # home, remoteの公開鍵をサーバに登録（公開鍵は事前に生成しておくこと）
  put(path, '/home/%s/.ssh/vps.pub' % (user_name))
  sudo('cat /home/%s/.ssh/vps.pub >>  /home/%s/.ssh/authorized_keys' % (user_name, user_name), user=user_name)
  # sshd再起動
  run("sshd -t")
  run("service sshd restart", pty=False)

def setup_iptables(ssh_port):
  # 接続済の通信は全て許可（必須）
  run("iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT")
  # ローカルループバックアドレスを許可（必須）
  run("iptables -A INPUT -i lo -j ACCEPT")
  # ICMPを許可（任意） ←  pingできなくても良い場合はコメントアウトしよう
  run("iptables -A INPUT -p icmp -j ACCEPT")
  # 各種攻撃対策
  run("iptables -A INPUT -s 10.0.0.0/8     -j DROP")
  run("iptables -A INPUT -d 10.0.0.0/8     -j DROP")
  run("iptables -A INPUT -s 172.16.0.0/12  -j DROP")
  run("iptables -A INPUT -d 172.16.0.0/12  -j DROP")
  run("iptables -A INPUT -s 192.168.0.0/16 -j DROP")
  run("iptables -A INPUT -d 192.168.0.0/16 -j DROP")
  run("iptables -A INPUT -f -j DROP")
  run("iptables -A INPUT -p tcp -m state --state NEW ! --syn -j DROP")
  run("iptables -A INPUT -p tcp --dport 113 -j REJECT --reject-with tcp-reset")
  run("iptables -A INPUT -p icmp --icmp-type echo-request -m hashlimit --hashlimit 1/s --hashlimit-burst 5 --hashlimit-mode srcip --hashlimit-name input_icmp  --hashlimit-htable-expire 300000 -j DROP")
  # SSHの許可設定
  run("iptables -A INPUT -p tcp -m tcp --dport %s -j ACCEPT"  % (ssh_port))
  # SSH以外の許可設定
  # 例えばWebサーバの場合、80番を許可する
  run("iptables -A INPUT -p tcp -m tcp --dport 80 -j ACCEPT")
  # デフォルトポリシーの設定
  run("iptables -P INPUT   DROP")
  run("iptables -P OUTPUT  ACCEPT")
  run("iptables -P FORWARD DROP")
  # 現在の状態を出力して、設定を保存・反映
  run("iptables -L --line-numbers -n")
  run("service iptables save")
  run("service iptables restart")

def yum_update():
  # システムの最新化
  run("yum -y update")
  # システムの自動更新
  run("yum -y install yum-cron")
  run("service yum-cron start")
  run("chkconfig yum-cron on")

def stop_ipv6():
  # IPv6の無効化
  run('echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf')
  run('echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.conf')
  run('sysctl -p', warn_only=True)
  run('ifconfig')
  # PostfixのIPv6無効化
  run("sed -i 's/^inet_protocols\s\+=\s\+all$/inet_protocols = ipv4/' /etc/postfix/main.cf")

def stop_service():
  def _stop(service_name):
    run('service %s stop' % (service_name))
    run('chkconfig %s off' % (service_name))
  _stop('ip6tables')

def set_root_address(root_address):
  if root_address != '':
    run('echo "root: %s" >> /etc/aliases'  % (root_address))
    run('newaliases')

# さくらのVPSで通信速度を向上させる
# 参考URL: https://help.sakura.ad.jp/app/answers/detail/a_id/1368
def speedup_network_sakura_vps():
    run("ethtool -K eth0 tso off")
    run('echo "ACTION==\"add\", SUBSYSTEM==\"net\", KERNEL==\"eth0\", RUN+=\"/sbin/ethtool -K eth0 tso off\"" > /etc/udev/rules.d/50-eth_tso.rules')
