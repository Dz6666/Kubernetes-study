from git.repo import Repo
import os, time
from git.repo.fun import is_git_dir
import subprocess
# from tools.sendMessageToDD import sendMessage


class GitRepository(object):
    """
        实现Git仓库自动管理
    """
    def __init__(self, local_path, repo_url, branch='develop'):
        self.local_path = local_path
        self.repo_url = repo_url
        self.repo = None
        self.initial(repo_url, branch)
        # self.commitMessage = commitMessage

    def initial(self, repo_url, branch):
        """
        初始化git仓库
        """
        if not os.path.exists(self.local_path):
            os.makedirs(self.local_path)
        
        git_local_path = os.path.join(self.local_path, '.git')
        if not is_git_dir(git_local_path):
            self.repo = Repo.clone_from(repo_url, to_path=self.local_path, branch=branch)
        else:
            self.repo = Repo(self.local_path)

    def pull(self):
        """
        从线上拉最新代码
        :return:
        """
        self.repo.git.pull()

    def branches(self):
        """
        获取所有分支
        :return:
        """
        branches = self.repo.remote().refs
        return [item.remote_head for item in branches if item.remote_head not in ['HEAD', ]]

    # def commits_log(self):
    #     """
    #     获取所有提交记录
    #     :return:
    #     """
    #     commit_log = Repo.git.log('--pretty={"commit":"%h","author":"%an","summary":"%s","date":"%cd"}', max_count=50,
    #                       date='format:%Y-%m-%d %H:%M')
    #     log_list = commit_log.split("\n")
    #     return [eval(item) for item in log_list]

    def add(self):
        #cmd = "git add ." + self.local_path
        cmd = "git add ."
        process = subprocess.Popen(cmd, shell=True)
        process.wait()
        returnCode = process.returncode
        if returnCode != 0:
            print(" add returnCode", returnCode)
        else:
            self.commit()

    def push(self):
        cmd = "git push"
        process = subprocess.Popen(cmd, shell=True)
        process.wait()
        returnCode = process.returncode
        if returnCode != 0:
            print("push returnCode", returnCode)
        else:
            # sendMessage({
            #     "fileName": "api文档 : \n\n已更新，请注意查看！ \n" +"\n更新信息: {}".format(
            #         commitMessage),
            #     "text": time.strftime("%Y/%m/%d %H:%M"),
            #     "error": False
            # })
            pass
    def commit(self):
        msg = input("输入提交commit信息:") 
        commitMessage=time.strftime("%Y/%m/%d %H:%M") + '-' + msg
        cmd = "git commit -m  '{}'".format(commitMessage)
        process = subprocess.Popen(cmd, shell=True)
        process.wait()
        self.push()


    def tags(self):
        """
        获取所有tag
        :return:
        """
        return [tag.name for tag in self.repo.tags]

    def change_to_branch(self, branch):
        """
        切换分支
        :param branch:
        :return:
        """
        self.repo.git.checkout(branch)

    def change_to_commit(self, branch, commit):
        """
        切换commit
        :param branch:
        :param commit:
        :return:
        """
        self.change_to_branch(branch=branch)
        self.repo.git.reset('--hard', commit)

    def change_to_tag(self, tag):
        """
        切换tag
        :param tag:
        :return:
        """
        self.repo.git.checkout(tag)

if __name__ == '__main__':
    # local_path = os.path.join('codes', 't1')
    local_path = os.path.join('/root/cmdb/')
    remote_path = 'https://github.com/Dz6666/Kubernetes-study.git'
    repo = GitRepository(local_path,remote_path)
    branch_list = repo.branches()
    print(branch_list)
    # 分支切换
    # repo.change_to_branch('develop')
    try:
        repo.pull()
        repo.add()
    except:
        print('提交失败')

