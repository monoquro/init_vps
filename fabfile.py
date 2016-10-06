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
