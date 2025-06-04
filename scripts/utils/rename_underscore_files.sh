#!/bin/bash
# Rename files with underscores to use hyphens in a2-docs directory

cd /home/waragainstwork/A2/a2-docs

echo "🔄 Renaming files from underscores to hyphens..."
echo ""

renamed_count=0

for file in *_*.md; do
    if [ -f "$file" ]; then
        newname=$(echo "$file" | tr '_' '-')
        if [ "$file" != "$newname" ]; then
            mv "$file" "$newname"
            echo "✓ Renamed: $file → $newname"
            ((renamed_count++))
        fi
    fi
done

echo ""
echo "✅ Renamed $renamed_count files"