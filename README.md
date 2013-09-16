# CS Python Course Manager

`c(s, py | man)` is The _CS Python Course Manager_ is module used to automate multiple teaching actions related to assignment submission, website publishing and logging.

###Setup & Installation
`c(s, py | man)` is based on the the [git_hook](https://github.com/alghanmi/git_hook) Flask app. For installation and setup instructions, follow the stepd outlined in that repo's [readme](https://github.com/alghanmi/git_hook/blob/master/README.md) file.


###Configuration
  + `cspy_man.uwsgi.ini` - used to deploy the webapp
  + `cspy_man.conf.ini` - used to configure the app behaviours

##Implemented Services:
### Website Deploy `/deploy`
This is written as a git [post-receive hook](https://help.github.com/articles/post-receive-hooks). Note that this hook expects the GitHub [JSON payload](https://help.github.com/articles/post-receive-hooks#the-payload).
