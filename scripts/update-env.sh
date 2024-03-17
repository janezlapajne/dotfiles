#!/usr/bin/env bash
#
# Update .env.example file from .env file

# Create example from .env file
# Define the input and output files
input_file=".env"
output_file=".env.example"

# Add warnining to the file
echo "################################################
# Example ".env" file
# Use command:  $ tail -n +7 .env.example > .env
# -> to create .env file from .env.example
################################################ " >$output_file
echo "" >>$output_file

# Create the example file
while IFS='=' read -r key value; do
	# if comment
	if [[ $key == \#* ]]; then
		echo "$key" >>"$output_file"
	# if key is not empty:
	elif [[ -n $key ]]; then
		echo "$key=" >>"$output_file"
	else
		echo "" >>"$output_file"
	fi
done <"$input_file"
