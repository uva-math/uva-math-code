#!/bin/zsh

# Iterate over the directories
for dir in algebra ancommons colloq diffeq galois geometry gradsem mathclub mathphys ntsem probability sotoa topology; do
  # Create the 2023-24 file
  touch "${dir}/${dir}23_24.html"

  # Copy content of the original file to the new one
  cp "${dir}/${dir}22_23.html" "${dir}/${dir}23_24.html"

  # Find and replace the archive line in the new file
  sed -i '' 's|<a href="/seminars/'${dir}'/">upcoming</a> | <a href="/seminars/'${dir}'/2022-23/">2022-23</a>|<a href="/seminars/'${dir}'/">upcoming</a> | <a href="/seminars/'${dir}'/2023-24/">2023-24</a> | <a href="/seminars/'${dir}'/2022-23/">2022-23</a>|' "${dir}/${dir}23_24.html"

  # Update the title, layout, permalink, show_from and show_to for 2023-24 in the new file
  sed -i '' 's|2022-23|2023-24|' "${dir}/${dir}23_24.html"
  sed -i '' 's|permalink: /seminars/'${dir}'/2022-23/|permalink: /seminars/'${dir}'/2023-24/|' "${dir}/${dir}23_24.html"
  sed -i '' 's|show_from='\''1 July 2022'\''|show_from='\''1 July 2023'\''|' "${dir}/${dir}23_24.html"
  sed -i '' 's|show_to='\''1 July 2023'\''|show_to='\''1 July 2024'\''|' "${dir}/${dir}23_24.html"
done
