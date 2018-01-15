# run this script before to initialize all needed things for app to run correctly
# yooho akhirnya

import util
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initializer untuk unma web admin app")
    parser.add_argument('database_url', type=str, help="URL untuk koneksi database. e.g. mysql+pymysql://uname:password@server")
    parser.add_argument('database_name', type=str, help="Nama database")
    parser.add_argument('upload_folder', type=str, help="Folder dimana file upload akan disimpan.")
    parser.add_argument('fcm_server_key', type=str, help="Firebase server key.")
    args = parser.parse_args()

    print("----- Saving FCM server key -----")
    util.gen_fcm_config(args.fcm_server_key)

    print("----- App Directories Generation -----")
    util.gen_app_dirs(args.upload_folder)

    print("----- Database Generation -----")
    util.gen_db(args.database_url, args.database_name)

    print("=== Berhasil, berhasil, berhasil... Yey :) ===")
