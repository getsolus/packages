#!/bin/bash

affected=""

for i in `find . -maxdepth 2 -name .git`; do
    nom="$(dirname ${i})"
    outp=`git -c color.ui=always -C "$nom" log -1 --pretty=format:"%C(yellow)%h%Creset %ad | %Cgreen%s%Creset %Cred%d%Creset %Cblue[%an]%Creset" --date=short  --after=@{7.days.ago}`
    if [[ -z "${outp}" ]]; then
        continue
    fi
    affected="${affected}\n\t - ${nom}"
    echo -e "\n\n${nom} -------\n"
    echo "$outp"
done

echo "Affected in last 7 days"
echo -e "${affected}"|sort|uniq
