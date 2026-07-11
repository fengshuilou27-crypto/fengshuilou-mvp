# -*- coding: utf-8 -*-
import sys
import json

# Force UTF-8 for stdout
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# Run the extraction script
exec(open('extract_professional_data.py', encoding='utf-8').read())
