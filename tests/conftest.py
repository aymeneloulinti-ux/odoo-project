import sys
import os
# make src importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import logging

# ensure root logger prints to console during tests
logging.getLogger().setLevel(logging.INFO)
