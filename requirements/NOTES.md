# Updating dependencies

pur -r base.txt ; pur -r local.txt ; pur -r production.txt ; pur -r test.txt
pip install -r base.txt --upgrade; pip install -r local.txt --upgrade; pip install -r production.txt --upgrade; pip install -r test.txt --upgrade
