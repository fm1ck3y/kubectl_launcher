#!/usr/bin/env bash
set -e

echo -e "\n---Getting job-launcher full name---"
NAME="$(python3 setup.py --name)"
VERSION="$(python3 setup.py --version)"
FULLNAME="$(python3 setup.py --fullname)"
echo "NAME: $NAME"
echo "VERSION: $VERSION"
echo "FULLNAME: $FULLNAME"

echo -e "\n---Building job-launcher python executable archive---"
rm -rfv "$FULLNAME"
python3 setup.py sdist bdist_wheel
pip3 install -t "$FULLNAME" -f dist "${NAME}==$VERSION"
find "$FULLNAME" -type d -regex '.*/__pycache__\|.*\.egg-info' -prune -exec rm -rf {} \;
python3 -m zipapp "$FULLNAME" --main 'kubectl_launcher.main:main' --python '/usr/bin/env python3' --output "${FULLNAME}.pyz"
