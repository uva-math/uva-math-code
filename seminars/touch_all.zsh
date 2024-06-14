#!/bin/zsh

# Define the base directory to start the recursive search
base_dir="$1"

# Check if the base directory is provided
if [ -z "$base_dir" ]; then
    echo "Usage: $0 <base_directory>"
    exit 1
fi

# Use find to search for all files and touch them
find "$base_dir" -type f -exec touch {} +

# Confirm completion
echo "Touched all files in the directory: $base_dir"
