#!/bin/bash

WEBSITE_REPO=/home/rami/course_website
LOG_FILE=/home/rami/course_website.log
SCRIPT_TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)

SSH_REMOTE_USER='csci201'
SSH_REMOTE_SERVER='aludra.usc.edu'
SSH_REMOTE_IDENTITY=/home/rami/.ssh/alghanmi-bot
SSH_REMOTE_COMMAND='umask 022 && source /usr/usc/git/default/setup.csh && cd public_html && git pull --quiet'

#Access Repo and make up to date
cd $WEBSITE_REPO
git checkout --quiet master
git pull --quiet
GIT_COMMENT_MASTER=$(git log -1 --format="commit %h by %aN on %ad")
rm -rf $WEBSITE_REPO/_site

#Build the website
jekyll build
mv _site /tmp/_site_${SCRIPT_TIMESTAMP}

#Switch to deploy branch & commit website updates
git checkout --quiet deploy
git pull --quiet
rsync -a /tmp/_site_${SCRIPT_TIMESTAMP}/ .
git add --all
git commit --quiet -m "Auto Build @ $SCRIPT_TIMESTAMP from master branch $GIT_COMMENT_MASTER "
git push --quiet

#Cleanup
git checkout --quiet master
rm -rf /tmp/_site_${SCRIPT_TIMESTAMP}/

#Pull deploy repo on web server
ssh -l $SSH_REMOTE_USER $SSH_REMOTE_SERVER -i $SSH_REMOTE_IDENTITY $SSH_REMOTE_COMMAND
