Overview
========

Simple backup script that takes a list of directories, converts each one to a zip file, 
and uploads them all to the given Amazon Glacier vault.

Usage
=====

This utility has three components:

* The ``backup.py`` script
* The ``glacier.ini`` config file
* The ``glacier.log`` log file

The first two must exist in the same directory, and the third will be auto-created when
the utility is run.

In order to get up and running, do the following:

1. Create a vault via the AWS Glacier web UI or API.
2. Create a user identity via IAM and set the policy so that it has write access to the
vault you just created. 
3. Grab the access id and secret key for the newly-created identity and plug them into the 
``glacier.ini`` file (see the sample included in this repo).
4. Fill out the remaining settings listed in the sample ``glacier.ini`` config file.
5. Run the ``backup.py`` script.
 
