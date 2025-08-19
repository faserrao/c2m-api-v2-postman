# restores from backup made above
cp Makefile.bak Makefile

# or strip the appended bit safely (creates Makefile.strip.bak)
sed -i.strip.bak -E 's/[[:space:]]*\|\s*\$\((FORCE_REBUILD|FORCE)\)//' Makefile

