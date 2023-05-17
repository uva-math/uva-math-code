#!/bin/zsh

# Iterate over the directories
for dir in algebra ancommons colloq diffeq galois geometry gradsem mathclub mathphys ntsem probability sotoa topology; do
  # Create the 2023-24 file
  touch "${dir}/${dir}23_24.html"

  # Copy content of the original file to the new one
  cp "${dir}/${dir}22_23.html" "${dir}/${dir}23_24.html"

  # Update the archive line, title, layout, permalink, show_from and show_to for 2023-24 in the new file
  sed -i '' -e 's|<a href="/seminars/'${dir}'/">upcoming</a> | <a href="/seminars/'${dir}'/2022-23/">2022-23</a>|<a href="/seminars/'${dir}'/">upcoming</a> | <a href="/seminars/'${dir}'/2023-24/">2023-24</a> | <a href="/seminars/'${dir}'/2022-23/">2022-23</a>|g' \
  -e 's|2022-23|2023-24|g' \
  -e 's|show_from='\''1 July 2022'\''|show_from='\''1 July 2023'\''|g' \
  -e 's|show_to='\''1 July 2023'\''|show_to='\''1 July 2024'\''|g' "${dir}/${dir}23_24.html"
done
