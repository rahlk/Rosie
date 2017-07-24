#!/bin/bash

# Reads the files in the demofiles directory and prints out a listing
# of the dependencies in the files in a format that graphviz can understand
# USE http://www.webgraphviz.com/

files=(./demofiles/*)
for i in "${files[@]}"
do

  # Run rosie, clean up the '.' style naming convention which doesn't play nice with
  # jq, traverse through the json output and pull out all the dependencies_text 
  # fields and then change the seperator character from '\n' to '~'
  DEPS=$(rosie -wholefile -encode json java.dependencies $i | sed 's/java\.//g' | jq '.[].subs[].dependencies_single.subs[].dependencies_text.text' | tr '\n' '~')
  IFS='~'
  read -a arrDEPS <<< "$DEPS"

  # Print out the results in a format graphviz can understand
  for j in "${arrDEPS[@]}"
  do
    echo "$i -> $j" | sed 's/\.java//g' | sed "s/\.\/demofiles\///g"
  done
done
