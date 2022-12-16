#!/usr/python3
import os
import sys
import shutil
import subprocess
import datetime
import json
import argparse

class SyncService():
    def __init__(self) -> None:
        with open('./config.json', 'r') as f:
            self.data = json.load(f)
        self.get_base_path()
        self.content_path = self.path_rep(self.base_path + 'wn/')
        self.git_path = self.base_path + 'wn_git/'
        self.remote_path = self.data['remote_path']
        self.date = datetime.datetime.now().date()
        self.today = "%d-%02d-%02d" % (self.date.year, self.date.month, self.date.day)

    def _run(self, cmd):
        print(cmd)
        ret = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        # ret = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            logs = [item.decode('utf8') for item in ret.stdout.readlines()]
        except:
            logs = [item.decode('gb2312') for item in ret.stdout.readlines()]
        # logs2 = [item for item in ret.stderr.readlines()]
        print(logs)
        # print(logs2)
        return logs

    def cyg_path_rep(self, path):
        if self.sys_str == 'Windows':
            # need cwrsync: https://cwrsync.apponic.com/download/
            return '/cygdrive/' + path.replace(":", '').replace('\\', '/') + '/'
        else:
            return path

    def _copy(self, src, dst):
        self._run('rsync -rv %s %s --exclude .git' % (self.cyg_path_rep(src), self.cyg_path_rep(dst)))

    def _remote_exist(self):
        without_ssh_path = self.remote_path.replace('ssh://', '')
        remote_ip = without_ssh_path.split('/')[0].split(':')[0]
        remote_port = without_ssh_path.split('/')[0].split(':')[1]
        remote_path = without_ssh_path.replace(remote_ip + ':' + remote_port, '')
        res = self._run('ssh -p %s %s ls %s' % (remote_port, remote_ip, remote_path))
        return len(res) > 0

    def path_rep(self, path):
        if self.sys_str == 'Windows':
            return path.replace('/', '\\')
        else:
            return path

    def get_base_path(self):
        res = self._run('uname -a')
        sys_str = 'windows'
        if 'MSYS_NT' in res[0]:
            self.sys_str = 'Windows'
            self.base_path = self.path_rep(self.data['Windows_base_path'])
        elif 'Microsoft' in res[0]:
            self.sys_str = 'wsl'
            self.base_path = self.path_rep(self.data['wsl_base_path'])
        elif 'Darwin' in res[0]:
            self.sys_str = 'macOS'
            self.base_path = self.path_rep(self.data['macOS_base_path'])
    
    def init(self):
        if not os.path.exists(self.content_path):
            print('error, path not exist.')
            return -1
        if not os.path.exists(self.git_path):
            print('git path not exist.')
            self._copy(self.content_path, self.git_path)
            self._run('cd %s && git init' % self.git_path)
            self._run('cd %s && git add . && git commit -m "%s daily upload, upload by %s"' %
                (self.git_path, self.today, self.sys_str))
            self._run('cd %s && git remote add %s' % (self.git_path, self.remote_path))
        else:
            pass
        return 0

    def push(self):
        # 如果内容不存在，报错退出
        if not os.path.exists(self.content_path):
            print('error, path not exist.')
            return -1
        # 如果git仓库不存在，初始化仓库
        if not os.path.exists(self.git_path):
            if not self._remote_exist():
                # 新建仓库
                self.init()
            else:
                # 把仓库当中的内容拉下来
                self.pull()
        # 复制文件
        self._copy(self.content_path, self.git_path)
        # 比较日期
        latest_log_date = self._run('cd %s && git log --no-color -n1 --oneline' % (self.path_rep(self.git_path), ))
        print(latest_log_date)
        y, m, d = [int(item) for item in latest_log_date[0].split(' ')[-6].split('-')]
        ny, nm, nd = self.date.year, self.date.month, self.date.day
        if ny != y or nm != m or nd != d:
            # 需要重新搞一个commit出来
            self._copy(self.content_path, self.git_path)
            self._run('cd %s && git add . && git commit -m "%s daily upload, upload by %s"' %
                (self.path_rep(self.git_path), self.today, self.sys_str))
        else:
            # 需要重新搞一个commit出来
            print('today you have upload another patch')
            self._copy(self.content_path, self.git_path)
            self._run('cd %s && git add . && git commit -m "%s daily upload, upload by %s"' %
                (self.path_rep(self.git_path), self.today, self.sys_str))
        
        self._run('cd %s && git remote remove origin' % (self.path_rep(self.git_path)))
        self._run('cd %s && git remote add origin %s' % (self.path_rep(self.git_path),
            self.remote_path))
        self._run('cd %s && git pull origin master' % (self.path_rep(self.git_path)))
        return 0

    def pull(self):
        # 如果仓库不存在，下载仓库
        if not os.path.exists(self.git_path):
            self._run('cd %s && git clone %s' % (self.base_path, self.remote_path))
            self._run('cd %s && git pull origin master' % (self.git_path))
        # 如果内容不存在，下载内容
        if not os.path.exists(self.content_path):
            os.mkdir(self.content_path)
        # 复制git当中的到目标位置
        self._copy(self.git_path, self.content_path)


def main():
    ss = SyncService()
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--download", help="download data", action="store_true")
    parser.add_argument("-u", "--upload", help="upload data", action="store_true")
    args = parser.parse_args()
    print(args)
    if args.download:
        ss.pull()
    elif args.upload:
        ss.push()

if __name__ == '__main__':
    # ss.pull()
    main()