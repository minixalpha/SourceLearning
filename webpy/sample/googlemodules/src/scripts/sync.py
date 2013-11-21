# Author: Alex Ksikes 
import os

cmd = "rsync -Puzav --exclude='config.py' --exclude='.git' dana:/googlemodules/scripts/"
os.system(cmd)
