#!/usr/bin/env sh

# Create example from .env file
# Define the input and output files
input_file=".env"
output_file=".env.example"

# Add warnining to the file
echo "################################################
# Example ".env" file 
# Use command:  $ tail -n +7 .env.example > .env
# -> to create .env file from .env.example
################################################ \n" >$output_file

# Create the example file
while IFS='=' read -r key value; do
	# if key and value not empty:
	if [ -n "$key" ] && [ -n "$value" ]; then
		echo "$key=" >>$output_file
	# if comment
	elif case $key in \#*) true ;; *) false ;; esac then
		echo "$key" >>$output_file
	else
		echo "" >>$output_file
	fi
done <"$input_file"
