#!/bin/bash
echo "=== Push to GitHub ==="
echo "1. First, create token at https://github.com/settings/tokens"
echo "2. Then create repo at https://github.com/Raven1628/pharmacogenomic-atlas"
echo ""
echo "Enter your GitHub Personal Access Token:"
read -s TOKEN

git push https://Raven1628:${TOKEN}@github.com/Raven1628/pharmacogenomic-atlas.git main
