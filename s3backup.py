import boto3
import getopt
import sys
import datetime
import json
from dateutil.tz import tzutc

# parametros de config
S3_BUCKET_NAME = 'nome_bucket'
S3_BACKUP_FOLDER = 'backup/'
LOCAL_WORKING_DIR = './'

# cli usage info
USAGE_INFO = 'usage: s3backup.py -o <operação> <outros_comandos>\n\toperações disponiveis: download, upload, list, ' \
             'delete e delete-all '
USAGE_INFO_DOWNLOAD = 'usage: s3backup.py -o download -f <arquivo>'
USAGE_INFO_UPLOAD = 'usage: s3backup.py -o upload -f <arquivo>'
USAGE_INFO_DELETE = 'usage: s3backup.py -o delete -f <arquivo>'
USAGE_INFO_DELETE_ALL = 'usage: s3backup.py -o delete-all -k <numero_arquivos_manter>'

# operações
SHORT_OPT = "ho:f:k:"
LONG_OPT = ["help", "operation=", "file=", "keep="]


def main(argv):
    try:
        opts, args = getopt.getopt(argv, SHORT_OPT, LONG_OPT)
    except getopt.GetoptError:
        print(USAGE_INFO)
        exit()
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(USAGE_INFO)
            exit()
        elif opt in ("-o", "--ofile"):
            if str(arg).lower() == "upload":
                upload_backup(argv)
                exit()
            elif str(arg).lower() == "download":
                download_backup(argv)
                exit()
            elif str(arg).lower() == "delete":
                delete_backup(argv)
                exit()
            elif str(arg).lower() == "delete-all":
                delete_all_backup(argv)
                exit()
            elif str(arg).lower() == "list":
                print(json.dumps([bkp.to_json() for bkp in list_backup()], indent=2))
                exit()
    print(USAGE_INFO)
    exit()


def upload_backup(argv):
    file = ''
    opts, args = getopt.getopt(argv, SHORT_OPT, LONG_OPT)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(USAGE_INFO_UPLOAD)
            exit(2)
        if opt in ("-f", "--file"):
            file = arg

    if file == '':
        print(USAGE_INFO_UPLOAD)
        sys.exit()

    ofile = S3_BACKUP_FOLDER + file

    s3 = boto3.client('s3')
    s3.upload_file(LOCAL_WORKING_DIR + file, S3_BUCKET_NAME, ofile)


def download_backup(argv):
    file = ''
    opts, args = getopt.getopt(argv, SHORT_OPT, LONG_OPT)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(USAGE_INFO_DOWNLOAD)
            exit()
        if opt in ("-f", "--file"):
            file = arg

    if file == '':
        print(USAGE_INFO_DOWNLOAD)
        sys.exit()

    dfile = S3_BACKUP_FOLDER + file

    s3 = boto3.client('s3')
    s3.download_file(S3_BUCKET_NAME, dfile, LOCAL_WORKING_DIR + file)


def delete_backup(argv):
    file = ''
    opts, args = getopt.getopt(argv, SHORT_OPT, LONG_OPT)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(USAGE_INFO_DELETE)
            exit()
        if opt in ("-f", "--file"):
            file = arg

    if file == '':
        print(USAGE_INFO_DELETE)
        sys.exit()

    s3 = boto3.client('s3')
    s3.delete_object(Bucket=S3_BUCKET_NAME, Key=S3_BACKUP_FOLDER + file)


def delete_all_backup(argv):
    keep = 0
    opts, args = getopt.getopt(argv, SHORT_OPT, LONG_OPT)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(USAGE_INFO_DELETE_ALL)
            exit()
        if opt in ("-k", "--keep"):
            keep = int(arg)

    s3 = boto3.client('s3')
    backups = list_backup()

    if keep > len(backups):
        return

    if keep > 0:
        backups = backups[:len(backups) - keep]

    for backup in backups:
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=backup.file)


def list_backup():
    s3 = boto3.client('s3')
    response = s3.list_objects(Bucket=S3_BUCKET_NAME)

    backups = list()

    if 'Contents' in response:
        for content in response['Contents']:
            backups.append(Backup(content["Key"], content["LastModified"], content["Size"]))
    return backups


class Backup:
    def __init__(self, file, date, size):
        self.file = file
        self.date = date
        self.size = size

    def to_json(self):
        return {"file": self.file.replace(S3_BACKUP_FOLDER, ''),
                "date": self.date.strftime("%Y/%m/%d %H:%M:%S"),
                "size": self.size}


if __name__ == '__main__':
    main(sys.argv[1:])
