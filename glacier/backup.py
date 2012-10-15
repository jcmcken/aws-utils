from boto import glacier
import datetime
import logging
import os
from distutils import archive_util
from ConfigParser import RawConfigParser

# settings/connection info
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(APP_ROOT, 'glacier.ini')
LOGFILE= os.path.join(APP_ROOT, 'glacier.log')
open(LOGFILE, 'a').close()
DATE = str(datetime.datetime.now())
DESCRIPTION = "Created: %s" % DATE

# set up logging
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
handler = logging.FileHandler(LOGFILE)
handler.setFormatter(
    logging.Formatter('%(asctime)s %(levelname)s %(message)s')
)
LOG.addHandler(handler)

def get_config():
    parser = RawConfigParser()
    parser.read(os.path.join(APP_ROOT, 'glacier.ini'))
    config = parser._sections
    dirs = config['local']['backup_dirs'].split(os.linesep)
    dirs = map(lambda x: x.strip(), dirs)
    config['local']['backup_dirs'] = dirs
    return config

def main():
    config = get_config()

    LOG.info('initiating Glacier backup')
    LOG.info('AWS region: %s' % config['login']['aws_region'])
    LOG.info('currently in local directory: %s' % APP_ROOT)
    
    # get a connection to Glacier
    LOG.info('creating connection')
    try:
        conn = glacier.connect_to_region(
            config['login']['aws_region'],
            aws_access_key_id=config['login']['aws_access_key_id'],
            aws_secret_access_key=config['login']['aws_secret_access_key'],
        )
    except Exception, e:
        LOG.exception('connection failed, exception was:')
        raise SystemExit, 1
    LOG.info('connection successful')

    # get the vault handle
    LOG.info("grabbing handle for '%s' vault" % config['glacier']['vault'])
    try:
        vault = conn.get_vault(config['glacier']['vault'])
    except Exception, e:
        LOG.exception('could not get vault, exception was:')
        raise SystemExit, 1

    # do the uploading
    LOG.info('begin archive upload for all configured directories')
    for d in config['local']['backup_dirs']:
        archive_id = upload_directory_to_vault(d, vault)
        LOG.info('successfully created archive with archive ID: %s' % archive_id)
        
    LOG.info('done!')

def upload_directory_to_vault(directory, vault):
    # create a local zip, which will become the Glacier archive
    LOG.info('creating local zipfile of "%s"' % directory)
    try:
        zipfile = archive_util.make_zipfile(os.urandom(14).encode('hex'), directory)
    except Exception, e:
        LOG.exception('could not create local zipfile, exception was:')
        raise SystemExit, 1

    # create the Glacier archive
    LOG.info('starting archive upload')
    try:
        archive_id = vault.concurrent_create_archive_from_file(zipfile)
    except Exception, e:
        LOG.exception('could not create Glacier archive from local '
                      'zipfile "%s", exception was:' % zipfile)
        raise SystemExit, 1

    return archive_id

if __name__ == '__main__':
    main()

