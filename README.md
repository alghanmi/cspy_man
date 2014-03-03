# CS Python Course Manager

`c(s, py | man)` is The _CS Python Course Manager_ is module used to automate multiple teaching actions related to assignment submission, website publishing and logging.

###Setup & Installation
`c(s, py | man)` is based on the the [git_hook](https://github.com/alghanmi/git_hook) Flask app. For detailed installation and setup instructions, follow the steps outlined in that repo's [readme](https://github.com/alghanmi/git_hook/blob/master/README.md) file.

####Extra Packages
Due to issues with sending bulk email, we are currently using [Mandrill](https://mandrill.com/) and its API to send emails. To install Mandrill, you run:
```bash
sudo pip install mandrill
```

####Configuration
  + `cspy_man.uwsgi.ini` - used to deploy the webapp _( no need to edit this file )_
  + `cspy_man.conf.ini` - used to configure the app behaviours _( **must** edit )_

####Basic Setup
  1. Rename `cspy_man.conf.sample.ini` to `cspy_man.conf.ini`
  1. Update `cspy_man.conf.ini` to reflect your configuration
  1. Install [required software](https://github.com/alghanmi/git_hook#setup)
  1. Configure your [web server](https://github.com/alghanmi/git_hook/blob/master/README.md#nginx-configuration)
  ```nginx
location = /git { rewrite ^ /git/; }
location /git { try_files $uri @git; }
location @git {
      include uwsgi_params;
      uwsgi_param SCRIPT_NAME /git;
      uwsgi_modifier1 30;
      uwsgi_pass unix:/tmp/uwsgi-cspy_man.uwsgi.sock;
}

  ```
  1. Configure [supervisor](https://github.com/alghanmi/git_hook#supervisor-configuration)
  
  ```ini
[program:cspy_man]
command=/usr/local/bin/uwsgi --ini /home/www/usc.alghanmi.org/cspy_man/cspy_man.uwsgi.ini
directory=/home/www/usc.alghanmi.org/cspy_man
;user=www-data
numprocs=1
autostart=true
autorestart=true
stdout_logfile=/home/www/usc.alghanmi.org/logs/uwsgi-supervisord.log
redirect_stderr=true
stopsignal=INT
```

  1. Install `c(s, py | man)`
  
```bash
cd
git clone git@github.com:usc-csci104-spring2014/cspy_man.git
sudo chown -R $USER:www-data cspy_man
sudo mv cspy_man /home/www/usc.alghanmi.org/
```

##Implemented Services:
### Website Deploy `/deploy`
This is written as a git [post-receive hook](https://help.github.com/articles/post-receive-hooks). Note that this hook expects the GitHub [JSON payload](https://help.github.com/articles/post-receive-hooks#the-payload). When a commit is (or set of commits are) pushed to the repository, the following happens:
  1. The [head] commit is parsed.
  1. The `website_deploy.sh` script is executed.
  1. An email using the `website_deployed.txt` template is prepared

####Deployment script
`website_deploy.sh` is written to be compatible with `aludra.usc.edu` and must have the following variables properly set:
  + `$HOME` directory for the `www-data` user. You can set that by
```bash
sudo usermod -d /home/www www-data
```
  + `WEBSITE_REPO` - [course_website](https://github.com/usc-csci201-fall2013/course_website) git repo
    * `www-data` must have read/write access to the repo

```bash
git clone git@github.com:usc-csci104-spring2014/course_website.git
cd course_website
git checkout -b deploy remotes/origin/deploy
git checkout master
cd ..
export WORKSPACE=/home/www/usc.alghanmi.org/cspy_man_workspace
sudo mkdir -p $WORKSPACE
sudo mv course_website $WORKSPACE
sudo chown -R www-data:www-data $WORKSPACE
```

  + `SSH_REMOTE_USER` - username on `aludra`
  + `SSH_REMOTE_SERVER` - default: `aludra.usc.edu`
  + Generate SSH Keys for `www-data` (with **no passphrase**)

```bash
#Generate Keyparis
sudo su - www-data -c 'ssh-keygen -t rsa -b 4096 -C "www-data@$(hostname -f)"'
```

  + Add the public key to:
    * [GitHub](https://github.com/settings/ssh), and
    * aludra's authorized keys

```bash
sudo cat $(cat /etc/passwd | grep ^www-data | cut -d: -f6)/.ssh/id_rsa.pub
```

  + Disable Host Key Checking
  
```bash
sudo su - www-data -s /bin/bash -c 'echo -e "Host *\n\tStrictHostKeyChecking no" | tee -a $HOME/.ssh/config'
```

  + Setup git user profile for `www-data` to be a bot, in this case `alghanmi-bot`

```bash
sudo su - www-data -s /bin/bash -c 'git config --global user.name "alghanmi-bot"'
sudo su - www-data -s /bin/bash -c 'git config --global user.email "alghanmi+bot@usc.edu"'
sudo su - www-data -s /bin/bash -c 'git config --global core.editor vim'
sudo su - www-data -s /bin/bash -c 'git config --global merge.tool vimdiff'
sudo su - www-data -s /bin/bash -c 'git config --global core.autocrlf input'
sudo su - www-data -s /bin/bash -c 'git config --global push.default simple'
```

### Helpful Commands
  + Turn off the app and all its services
```
sudo service supervisor stop; sudo pkill -9 uwsgi
```
  + Check Running Services
```
ps -ef | grep -v 'tail -f' |  grep uwsgi && echo '' && ps -ef | grep -v 'tail -f' | grep super
```
  + Check Logs
```
sudo tail -f /home/www/usc.alghanmi.org/logs/error.log /home/www/usc.alghanmi.org/logs/access.log /home/www/usc.alghanmi.org/logs/uwsgi-supervisord.log /var/log/uwsgi/cspy_man.log  /var/log/uwsgi/cspy_man.uwsgi.log  /var/log/supervisor/cspy_man-*.log /var/log/supervisor/supervisord.log
```
  + Run script as another user
```
sudo su -c "bash /home/www/usc.alghanmi.org/cspy_man/scripts/website_deploy.sh" -s /bin/bash www-data
```

### Helpful aliases

```bash
alias cspystatus='sudo su - www-data -c '"'"'cd ~/usc.alghanmi.org/cspy_man; git status'"'"''
alias cspypull='sudo su - www-data -c '"'"'cd ~/usc.alghanmi.org/cspy_man; git pull'"'"''
```
