#!/bin/bash

#################################################################
#####  To make this email users, it is required to provide  #####
#####  file called "members" with users' email addresses    #####
#####  and AWS account able to call netw. interfaces API    #####
#################################################################

declare -i i=1;
list_environments=()

aws ec2 describe-network-interfaces --profile kainosmap --output text | grep ASSOCIATION > AWS_call
while read -r p; do
  set -- $p
  list_environments+=($4)
done <AWS_call

printf "%s\n" "${list_environments[@]}" > temp
awk 'NR%2==0' temp > remove_duplicats
sed '/34.237.139.39/d' remove_duplicats > no_jenkins_environments

while read -r p; do
  environment=$(sed "${i}q;d" no_jenkins_environments)
  if [ -z $environment ]; then
    echo "Only $[i-1] members out of $(wc -l < members) got assigned envs. Fix that!"
    break;
  fi
  i=i+1;
  echo "Hello dear geek. This is your environment's details: ${environment}:8080" | mail -s "Kainos map - Jmeter Workshops" $p
  echo "Member: $p, Env: $environment"
done <members
