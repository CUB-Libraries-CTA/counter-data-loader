from dataloader.jr1report import JR1Report
from dataloader.counterdb import Platform, Publisher, Publication, UsageStat
import sys, glob

def load_platform(jr1report):
    platform = Platform()
    platform.insert(jr1report.platform)

def load_publisher(jr1report):
    publisher = Publisher()
    for n in jr1report.data_range():
        publisher.insert(jr1report.get_row(n))

def load_publication(jr1report):
    publication = Publication()
    for n in jr1report.data_range():
        publication.insert(jr1report.get_row(n))

def load_usage(jr1report):
    usage = UsageStat()
    for n in jr1report.data_range():
        usage.insert(jr1report.get_row(n), jr1report.period_from, jr1report.period_to)

def log_error(err_msg):
    logfile = open('errors.log', 'a')
    logfile.write(err_msg + '\n')
    logfile.close()

if __name__ == "__main__":

    # Running this script requires a single argument representing
    # the directory containing the JR1 Excel reports.
    #
    # Given that there are JR1 reports to process, each in turn
    # will have data extracted and written to the database. Each
    # of the main database tables will be loaded in sequence to
    # ensure dependencies are maintained.
    if len(sys.argv) == 1:
        print('Usage: python jr1loader.py <report directory>')
    else:
        jr1dir = sys.argv[1]
        files = glob.glob('{}/*.xlsx'.format(jr1dir))
        for f in files:
            print(('Processing {}'.format(f)))

            # Begin processing individual JR1 reports. If something 
            # goes wrong, write a log entry and move on to the
            # next report.
            try:
                jr1report = JR1Report(f)
                load_platform(jr1report)
                load_publisher(jr1report)
                load_publication(jr1report)
                #load_usage(jr1report)
            except Exception as e:
                log_error('{0} | {1} | {2}'.format(f, str(sys.exc_info()[0]), str(sys.exc_info()[1])))
