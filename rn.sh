#!/bin/bash

# Loop through files starting with "lob"
for file in lob*; do
  # Check if file exists to avoid issues if no files match
  if [[ -e "$file" ]]; then
    newname="c2m${file:3}"
    echo "Renaming: $file -> $newname"
    mv "$file" "$newname"
  fi
done

