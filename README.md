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
