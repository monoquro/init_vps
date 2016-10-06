# -*- coding: UTF-8 -*-

from fabric.api import task, env, run

env.hosts = [env.ip]

u"""初期設定 `fab setup`"""
import tasks.setup as setup_
@task
def setup():
  def server_setup():
    setup_.server_setup(env)
    setup_.speedup_network_sakura_vps()
  server_setup()

u"""言語install with anyenv `fab anyenv`"""
import tasks.anyenv as anyenv_
@task
def anyenv():
  def install():
    anyenv_.install(env)
  install()

u"""nginx install `fab nginx`"""
import tasks.nginx as nginx_
@task
def nginx():
  def install():
    nginx_.install(env)
  install()
