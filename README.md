CentOS Setup tools
====

## Description

sakura vpsを想定し、CentOS6.5の設定を行う。

## Demo

## Requirement

## Usage

#### common

.fabricrcを作成する。

    ip = ${ip address}
    user = root
    password = ${password}
    root_mail = ${mail address}
    working_user = ${user}
    working_pwd = ${password}
    ssh_port = ${port}
    ssh_authorized_keys = ${pub file path}

#### task:setup

`fab setup`

vpsの初期設定を行います。
* env.working_user, env.working_pwdに基づき、userを作成する。
* security設定をする。
    * ssh loginをenv.ssh_authorized_keysのpub fileに記載されているkeyに制限する。

## Contribution

## Licence

[MIT](https://github.com/tcnksm/tool/blob/master/LICENCE)

## Author

[monoquro](https://github.com/monoquro)