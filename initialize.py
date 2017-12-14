# run this script before to initialize all needed things for app to run correctly
# yooho akhirnya

import util


print("----- App Directories Generation -----")
util.gen_app_dirs()

print("----- Database Generation -----")
util.gen_db()

print("=== Berhasil, berhasil, berhasil... Yey :) ===")
