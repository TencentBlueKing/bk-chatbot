"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云PaaS平台社区版 (BlueKing PaaSCommunity Edition) available.
Copyright (C) 2017-2018 THL A29 Limited,
a Tencent company. All rights reserved.
Licensed under the MIT License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import abc
import os
import sys
import argparse


class DockerFile(abc.ABC):
    def __init__(self):
        pass

    def add(self):
        pass

    def from_env(self, base_env: str):
        return f'FROM {base_env}\n'

    def work_dir(self, work_dir: str):
        return f'WORKDIR {work_dir}\n'

    def env(self, **kwargs):
        return '\n'.join(f'ENV {k.upper()}={v}' for k, v in kwargs.items())

    def copy(self, file: str = 'requirements.txt', dst_dir: str = './'):
        return f'COPY {file} {dst_dir}\n'

    def cmd(self):
        pass

    def entry_point(self, *args):
        cmd = f'ENTRYPOINT {list(args)}'
        return cmd.replace("'", '"')

    @staticmethod
    def set_timezone():
        return 'RUN rm -f /etc/localtime && ' \
               'ln -sv /usr/share/zoneinfo/Asia/Shanghai /etc/localtime ' \
               '&& echo "Asia/Shanghai" > /etc/timezone\n'

    @abc.abstractmethod
    def generate(self, cmdline_args: argparse.ArgumentParser):
        pass

    @abc.abstractmethod
    def cli(self, args):
        pass


class BotDockerFile(DockerFile):
    """
    1, use python script to generate dockerfile
    2, replace env to real value
    """
    BK_ENV_TEMPLATE = [
        'BK_APP_ID',
        'BK_APP_SECRET',
        'BK_BASE_TOKEN',
        'BK_PAAS_DOMAIN',
        'BK_CHAT_DOMAIN',
        'BK_CC_DOMAIN',
        'BK_JOB_DOMAIN',
        'BK_SOPS_DOMAIN',
        'BK_DEVOPS_DOMAIN',
        'BK_BASE_DOMAIN',
        'BK_ITSM_DOMAIN',
        'BK_CC_ROOT',
        'BK_JOB_ROOT',
        'BK_SOPS_ROOT',
        'BK_DEVOPS_ROOT',
        'BK_BASE_ROOT',
        'BK_ITSM_ROOT',
        'BACKEND_ROOT'
    ]

    JIRA_ENV_TEMPLATE = [
        'JIRA_ROOT',
        'JIRA_USER_EMAIL',
        'JIRA_TOKEN',
        'JIRA_DOMAIN',
    ]

    def __init__(self):
        super(BotDockerFile, self).__init__()

    @staticmethod
    def pip_install():
        return 'RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.tencent.com/pypi/simple/ ' \
               '&& pip install ujson msgpack -i https://mirrors.tencent.com/pypi/simple/\n'

    def set_bk_env(self, bk_env: str):
        all_bk_env = ''
        for env in bk_env.split(','):
            tmp = {f'{env}_{x}': '${' + f'{env.upper()}_{x}' + '}' for x in self.BK_ENV_TEMPLATE}
            all_bk_env += f'{self.env(**tmp)}\n'
        return all_bk_env

    def set_env(self, tag, **kwargs):
        tag_env = self.env(**{f'{tag}_{k}': v for k, v in kwargs.items()})
        return f'{tag_env}\n'

    def set_default_env(self, **kwargs):
        """
        set_default_env(helper=helper, extra_tool=extra_tool,
        intent_category=intent_category, guide_url=guide_url)
        """
        return self.set_env('DEFAULT', **kwargs)

    def set_plugin_env(self, **kwargs):
        """
        set_plugin_env(root=plugin_root, token=plugin_token)
        """
        return self.set_env('PLUGIN', **kwargs)

    def set_jira_env(self, **kwargs):
        """
        set_jira_env(root=jira_root, token=jira_token)
        """
        return self.set_env('JIRA', **kwargs)

    def set_aes_env(self, **kwargs):
        """
        set_aes_env(key=key, iv=iv)
        """
        return self.set_env('AES', **kwargs)

    def set_redis_env(self, **kwargs):
        """
        set_redis_env(db_name=db_name, db_port=db_port, db_password=db_password)
        """
        return self.set_env('REDIS', **kwargs)

    def set_es_env(self):
        """
        set_es_env(key=key, iv=iv)
        """
        pass

    def set_protocol_env(self, **kwargs):
        return f'{self.env(**kwargs)}\n'

    def generate(self, cmdline_args: argparse.ArgumentParser):
        flow = self.from_env(cmdline_args.base)
        flow += self.work_dir(cmdline_args.work_dir)
        flow += f'{self.env(product=cmdline_args.product)}\n'
        flow += f'{self.env(id=cmdline_args.id)}\n'
        flow += f'{self.env(host=cmdline_args.host)}\n'
        flow += f'{self.env(port=cmdline_args.port)}\n'
        flow += f'{self.env(api_root=cmdline_args.api_root)}\n'
        flow += f'{self.env(rtx_name=cmdline_args.rtx_name)}\n'
        flow += f'{self.env(nickname=cmdline_args.nickname)}\n'
        flow += f'{self.env(session_reserved_cmd=cmdline_args.reserved_cmd)}\n'
        default_env = self.set_default_env(helper=cmdline_args.helper,
                                           extra_tool=cmdline_args.extra_tool,
                                           intent_category=cmdline_args.intent_category,
                                           guide_url=cmdline_args.guide_url)
        flow += default_env
        flow += f'{self.env(bk_env=cmdline_args.bk_env)}\n'
        flow += f'{self.env(bk_super_username=cmdline_args.bk_super_username)}\n'
        flow += f'{self.set_bk_env(cmdline_args.bk_env)}\n'
        plugin_env = self.set_plugin_env(root=cmdline_args.plugin_root,
                                         token=cmdline_args.plugin_token)
        flow += plugin_env
        jira_env = self.set_jira_env(root=cmdline_args.jira_root,
                                     user_email=cmdline_args.jira_user_email,
                                     token=cmdline_args.jira_token,
                                     domain=cmdline_args.jira_domain)
        flow += jira_env
        aes_env = self.set_aes_env(key=cmdline_args.data_aes_key,
                                   iv=cmdline_args.data_aes_iv)
        flow += aes_env
        redis_env = self.set_redis_env(db_name=cmdline_args.redis_db_name,
                                       db_port=cmdline_args.redis_db_port,
                                       db_password=cmdline_args.redis_db_password)
        flow += redis_env
        protocol_env = self.set_protocol_env(corpid=cmdline_args.corpid,
                                             fwid=cmdline_args.fwid,
                                             service_id=cmdline_args.service_id,
                                             secret=cmdline_args.secret,
                                             token=cmdline_args.token,
                                             aes_key=cmdline_args.aes_key)
        flow += protocol_env
        flow += self.copy()
        flow += self.pip_install()
        flow += self.copy('.', '.')
        flow += self.set_timezone()
        flow += self.entry_point("python", "src/backend/server.py")

        if not os.path.isfile('./Dockerfile'):
            os.mknod('./Dockerfile')

        with open('./Dockerfile', 'w+') as f:
            f.write(flow)

    def cli(self, args):
        parser = argparse.ArgumentParser(description='generate dockerfile...')
        parser.add_argument('--base', required=True, help="base image")
        parser.add_argument('--work_dir', required=True, help="work dir")
        parser.add_argument('--product', required=True, help="product")
        parser.add_argument('--id', required=True, help="id")
        parser.add_argument('--host', required=True, help="host")
        parser.add_argument('--port', required=True, help="port")
        parser.add_argument('--api_root', required=True, help="api root")
        parser.add_argument('--rtx_name', required=True, help="rtx name")
        parser.add_argument('--nickname', required=True, help="nickname")
        parser.add_argument('--reserved_cmd', required=True, help="reserved cmd")
        parser.add_argument('--helper', required=True, help="helper")
        parser.add_argument('--extra_tool', required=True, help="extra_tool")
        parser.add_argument('--intent_category', required=True, help="intent category")
        parser.add_argument('--guide_url', required=True, help="guide url")
        parser.add_argument('--bk_env', required=True, help="bk_env")
        parser.add_argument('--bk_super_username', required=True, help="bk_super_username")
        parser.add_argument('--plugin_root', required=True, help="plugin root")
        parser.add_argument('--plugin_token', required=False, help="plugin token")
        parser.add_argument('--jira_root', required=False, help="jira root")
        parser.add_argument('--jira_user_email', required=False, help="jira user email")
        parser.add_argument('--jira_token', required=False, help="jira token")
        parser.add_argument('--jira_domain', required=False, help="jira domain")
        parser.add_argument('--data_aes_key', required=True, help="data aes key")
        parser.add_argument('--data_aes_iv', required=True, help="data aes iv")
        parser.add_argument('--redis_db_name', required=True, help="redis_db_name")
        parser.add_argument('--redis_db_port', required=True, help="redis_db_port")
        parser.add_argument('--redis_db_password', required=True, help="redis_db_password")
        parser.add_argument('--corpid', required=False, help="corpid")
        parser.add_argument('--fwid', required=False, help="fwid")
        parser.add_argument('--service_id', required=False, help="service_id")
        parser.add_argument('--secret', required=False, help="secret")
        parser.add_argument('--token', required=False, help="token")
        parser.add_argument('--aes_key', required=False, help="aes_key")
        cmdline_args = parser.parse_args(args)
        self.generate(cmdline_args)


if __name__ == '__main__':
    BotDockerFile().cli(sys.argv[1:])
