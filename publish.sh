#!/bin/bash

rm -rf .site
mkdir .site
cd .site/
git clone https://github.com/nanoflite/f3k_bk.git . -b gh-pages
cp -a ../site/* .
git add .
git commit -m"site update"
git push origin gh-pages
