# CS Python Course Manager

`c(s, py | man)` is The _CS Python Course Manager_ is module used to automate multiple teaching actions related to assignment submission, website publishing and logging.

###Setup & Installation
`c(s, py | man)` is based on the the [git_hook](https://github.com/alghanmi/git_hook) Flask app. For detailed installation and setup instructions, follow the steps outlined in that repo's [readme](https://github.com/alghanmi/git_hook/blob/master/README.md) file.

####Configuration
  + `cspy_man.uwsgi.ini` - used to deploy the webapp _( no need to edit this file )_
  + `cspy_man.conf.ini` - used to configure the app behaviours _( **must** edit )_

####Basic Setup
  1. Rename `cspy_man.conf.sample.ini` to `cspy_man.conf.ini`
  1. Update `cspy_man.conf.ini` to reflect your configuration
  1. Install [required software](https://github.com/alghanmi/git_hook#setup)
  1. Configure your [web server](https://github.com/alghanmi/git_hook/blob/master/README.md#nginx-configuration)
  1. Configure [supervisor](https://github.com/alghanmi/git_hook#supervisor-configuration)


##Implemented Services:
### Website Deploy `/deploy`
This is written as a git [post-receive hook](https://help.github.com/articles/post-receive-hooks). Note that this hook expects the GitHub [JSON payload](https://help.github.com/articles/post-receive-hooks#the-payload). When a commit is (or set of commits are) pushed to the repository, the following happens:
  1. The [head] commit is parsed.
  1. The `website_deploy.sh` script is executed.
  1. An email using the `website_deployed.txt` template is prepared

####Deployment script
`website_deploy.sh` is written to be compatible with `aludra.usc.edu` and must have the following variables properly set:
  + `WEBSITE_REPO` - [course_website](https://github.com/usc-csci201-fall2013/course_website) git repo
    * `www-data` must have read/write access to the repo
```shell
git clone git@github.com:usc-csci201-fall2013/course_website.git
cd course_website
git checkout -b deploy remotes/origin/deploy
git checkout master
cd ..
sudo mkdir -p /home/www/usc.alghanmi.org/cspy_man_workspace
sudo mv course_website /home/www/usc.alghanmi.org/cspy_man_workspace/
sudo chown -R www-data:www-data /home/www/usc.alghanmi.org/cspy_man_workspace/
```
  + `SSH_REMOTE_USER` - username on `aludra`
  + `SSH_REMOTE_SERVER` - default: `aludra.usc.edu`
  + `SSH_REMOTE_IDENTITY` - private ssh key to access aludra & GitHub with **no passphrase**
```shell
sudo mkdir -p /home/www/usc.alghanmi.org/cspy_man_workspace/.ssh
sudo chmod 700 /home/www/usc.alghanmi.org/cspy_man_workspace/.ssh

## Copy over the ssh keys to this location


echo '#!/bin/sh' | sudo tee /home/www/usc.alghanmi.org/cspy_man_workspace/ssh_git.sh
echo 'exec /usr/bin/ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i /home/www/usc.alghanmi.org/cspy_man_workspace/.ssh/alghanmi-bot "$@" > /dev/null' | sudo tee -a /home/www/usc.alghanmi.org/cspy_man_workspace/ssh_git.sh
sudo chmod 755 /home/www/usc.alghanmi.org/cspy_man_workspace/ssh_git.sh
sudo chown -R www-data:www-data /home/www/usc.alghanmi.org/cspy_man_workspace/
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
