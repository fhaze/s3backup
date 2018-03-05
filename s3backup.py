import boto3
import getopt
import sys

# parametros de config
S3_BUCKET_NAME = 'nome_bucket'
S3_BACKUP_FOLDER = 'backup/'
LOCAL_WORKING_DIR = './'

# cli usage info
USAGE_INFO = 'usage: s3backup.py -o <operação> <outros_comandos>\n\toperações disponiveis: download e upload'
USAGE_INFO_DOWNLOAD = 'usage: s3backup.py -o download -f <arquivo>'
USAGE_INFO_UPLOAD = 'usage: s3backup.py -o upload -f <arquivo>'

# operações
SHORT_OPT = "ho:f:"
LONG_OPT = ["help", "operation=", "file="]


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


if __name__ == '__main__':
    main(sys.argv[1:])
