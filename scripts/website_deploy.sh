#!/bin/bash

WORKSPACE=/home/www/usc.alghanmi.org/cspy_man_workspace
WEBSITE_REPO=$WORKSPACE/course_website
SCRIPT_TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)

SSH_REMOTE_USER='csci104'
SSH_REMOTE_SERVER='aludra.usc.edu'
SSH_REMOTE_COMMAND='umask 022 && source /usr/usc/git/default/setup.csh && cd public_html && git pull --quiet'

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

#Access Repo and make up to date
cd $WEBSITE_REPO
git checkout --quiet master
git pull --quiet
GIT_COMMENT_MASTER=$(git log -1 --format="commit %h by %aN on %ad")
rm -rf $WEBSITE_REPO/_site

#Build the website
echo "***** [LOG] Building The Website *****"
jekyll build
mv _site /tmp/_site_${SCRIPT_TIMESTAMP}

#Switch to deploy branch & commit website updates
git checkout --quiet deploy
git pull --quiet
rsync -a /tmp/_site_${SCRIPT_TIMESTAMP}/ .
git add --all
git diff-index --quiet HEAD || git commit --quiet -m "Auto Build @ $SCRIPT_TIMESTAMP from master branch $GIT_COMMENT_MASTER "
git push --quiet

#Cleanup
#echo "***** [LOG] Cleanup *****"
git checkout --quiet master
rm -rf /tmp/_site_${SCRIPT_TIMESTAMP}/

#Pull deploy repo on web server
#echo "**** [LOG] Deploying on Aludra *****"
ssh -l $SSH_REMOTE_USER $SSH_REMOTE_SERVER $SSH_REMOTE_COMMAND
