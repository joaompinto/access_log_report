# Generate summarized reports from access logs files

Main Features
-------------
- Handle large files with low memory usage by performing in-flight accounting
- Transparent support for compressed input files (.gz; bz2)
- Support for custom log formats (ACCESS_LOG_FMT environment variable)

Usage:
------
    acl2csv.py sample.cfg access_log > sample.csv
    acl2png.py sample.cfg sample.csv
    ls -ltr *.png