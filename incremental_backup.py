#! /usr/bin/env python

import datetime
import subprocess
import glob

BACKUP_DESTINATION = "/media/e5e5ebf0-96f2-431c-a615-34dc71ca02f4"
NOW = datetime.datetime.now()
BACKUP_FORMAT = "backup-%Y-%m-%d_%H:%M:%S"
# which day of the month to keep for monthlies:
MONTHLY_DATE_TO_KEEP = 28
# how many weeks of monthly backups to keep
WEEKS_TO_KEEP_MONTHLIES = 16
# how many days of daily backups to keep
DAYLIES_TO_KEEP = 7

# rsync everything starting at the filesystem root, ignoring other
# mounted filesystems, using hard links for files already found in
# --link-dest:
subprocess.call('rsync  -vaxAX --ignore-errors '
                '--link-dest={0}/current / {0}/{1}'.format(
        BACKUP_DESTINATION, NOW.strftime(BACKUP_FORMAT)), shell=True)

# TODO use python instead of subprocess to rm stuff
subprocess.call('rm -f {0}/current'.format(BACKUP_DESTINATION),
                shell=True)
subprocess.call('ln -s {0} {1}/current'.format(
        NOW.strftime(BACKUP_FORMAT), BACKUP_DESTINATION), shell=True)

# backup is done, now delete old ones

# OK, here's how this works.  Pick a magic date, DATE_TO_KEEP.  Every
# night, delete everything that is older than WEEKS_TO_KEEP weeks, and
# delete everything that is older than one week that is not the
# DATE_TO_KEEP.  That will keep around one week of nightly backups and
# WEEKS_TO_KEEP of monthly backups.

daily_backup_cutoff = NOW - datetime.timedelta(days=DAYLIES_TO_KEEP)

# I wish this were possible, but months are tricky (what is 6 months
# from the last day of a month?  you can't just add 6 to the month
# component of the date):
# four_months_ago = NOW - datetime.timedelta(months=4)
# so do this instead:
monthly_backup_cutoff = NOW - datetime.timedelta(weeks=WEEKS_TO_KEEP_MONTHLIES)

# turn string directory name into datetime object;
for filename in glob.glob('{0}/*'.format(BACKUP_DESTINATION)):
    if 'current' in filename:
        continue
    print 'deciding the fate of {0}'.format(filename)
    file_date = datetime.datetime.strptime(filename, '{0}/{1}'.format(
            BACKUP_DESTINATION, BACKUP_FORMAT))
    if file_date < monthly_backup_cutoff:
        print 'prior to {0}, delete it'.format(
            monthly_backup_cutoff.strftime('%Y-%m-%d_%H:%M:%S'))
        subprocess.call('rm -rf {0}'.format(filename), shell=True)
    if(file_date < daily_backup_cutoff and
       file_date.day != MONTHLY_DATE_TO_KEEP):
        print 'more than a week ago, but not the {0}th'.format(
            MONTHLY_DATE_TO_KEEP)
        subprocess.call('rm -rf {0}'.format(filename), shell=True)
