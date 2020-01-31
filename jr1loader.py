from dataloader.jr1report import JR1Report
from dataloader.counterdb import Platform, Publisher, Publication, UsageStat
import sys, glob
import traceback
from datetime import date

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

def write_error(err_msg):
    logfile = open('errors.log', 'at')
    logfile.write(err_msg + '\n')
    logfile.close()
    
def write_processed(line):
    logfile = open('processed.log', 'at')
    logfile.write('{}\n'.format(line))
    logfile.close()
    
def read_processed():
    processed = list()
    try:
        logfile = open('processed.log', 'rt')
        for line in logfile:
            processed.append(line.rstrip())
    except FileNotFoundError:
        logfile = open('processed.log', 'xt')
    logfile.close()
    return list(processed)

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
        
        # Get list of files that have already been processed
        processed = read_processed()

        # Begin processing individual JR1 reports. If something 
        # goes wrong, write a log entry and move on to the
        # next report.
        jr1dir = sys.argv[1]
        files = glob.glob('{}/*.xlsx'.format(jr1dir))
        for f in files:
            if f not in processed:
                print(('Processing {}'.format(f)))
                try:
                    # Run through the load routines sequentially
                    jr1report = JR1Report(f)
                    load_platform(jr1report)
                    load_publisher(jr1report)
                    load_publication(jr1report)
                    load_usage(jr1report)
                    
                    # Create a log entry for the file just processed
                    line = '{0},{1},{2},{3}'.format(
                        jr1report.filename,
                        jr1report.period,
                        date.isoformat(date.today()),
                        str(len(jr1report.data_range())))
                    write_processed(line)
                except Exception as e:
                    write_error('{0}\n{1}'.format(f, traceback.format_exc()))
