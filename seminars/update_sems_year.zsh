#!/bin/zsh

# Iterate over the directories  
for dir in algebra colloq diffeq galois geometry gradsem mathclub mathphys ntsem probability sotoa topology; do  
  # Create the 2025-26 file  
  touch "${dir}/${dir}25_26.html"

  # Copy content of the original file to the new one  
  cp "${dir}/${dir}24_25.html" "${dir}/${dir}25_26.html"

  # Update the archive line, title, layout, permalink, show_from and show_to for 2025-26 in the new file  
  sed -i '' \  
  -e 's#2024-25/$#2025-26/#g' \  
  -e 's#2024-25$#2025-26#g' \  
  -e 's#show_from='\''1 July 2024'\''#show_from='\''1 July 2025'\''#g' \  
  -e 's#show_to='\''1 July 2025'\''#show_to='\''1 July 2026'\''#g' "${dir}/${dir}25_26.html"

  for file in "${dir}"/*.html; do  
    sed -i '' -e "s#<a href=\"/seminars/${dir}/\">upcoming</a> | <a href=\"/seminars/${dir}/2024-25/\">2024-25</a>#<a href=\"/seminars/${dir}/\">upcoming</a> | <a href=\"/seminars/${dir}/2025-26/\">2025-26</a> | <a href=\"/seminars/${dir}/2024-25/\">2024-25</a>#g" "${file}"  
    sed -i '' -e '/<a href="\/seminars\/'${dir}'\/">upcoming<\/a> |$/{  
    N  
    s#<a href="\/seminars\/'${dir}'\/">upcoming<\/a> |\n<a href="\/seminars\/'${dir}'\/2024-25\/">2024-25<\/a>#<a href="\/seminars\/'${dir}'\/">upcoming<\/a> | <a href="\/seminars\/'${dir}'\/2025-26\/">2025-26<\/a> | <a href="\/seminars\/'${dir}'\/2024-25\/">2024-25<\/a>#g  
  }' "${file}"  
  done  
done
