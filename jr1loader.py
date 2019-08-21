from dataloader.jr1report import JR1Report
from dataloader.counterdb import Platform, Publisher
import sys, glob, os

platform = Platform()
publisher = Publisher()

def load_platform(jr1report):
    platform.insert(jr1report.platform)

def load_publisher(jr1report):
    for n in jr1report.data_range():
        publisher.insert(jr1report.get_row(n))

def log_error(err_msg):
    logfile = open('errors.log', 'a')
    logfile.write(err_msg + '\n')
    logfile.close()

if __name__ == "__main__":

    if len(sys.argv) == 1:
        print 'Usage: python jr1loader.py <report directory>'
    else:
        jr1dir = sys.argv[1]
        files = glob.glob(jr1dir + '/*.xlsx')
        for f in files:
            print 'Processing ' + f
            try:
                jr1report = JR1Report(f)
                load_platform(jr1report)
                load_publisher(jr1report)
            except:
                log_error(f + ' | ' + str(sys.exc_info()[0]) + ' | ' + str(sys.exc_info()[1]))
