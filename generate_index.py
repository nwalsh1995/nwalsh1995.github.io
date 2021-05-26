#!/usr/bin/env python3

#  Recursively generate index.html files for
#  all subdirectories in a directory tree

import datetime
import argparse
import fnmatch
import os
import sys


index_file_name = 'index.html'


def process_dir(top_dir, opts):
    for parentdir, dirs, files in os.walk(top_dir):
        if ".git" in parentdir:
            continue
        if not opts.dryrun:
            abs_path = os.path.join(parentdir, index_file_name)

            try:
                index_file = open(abs_path, "w")
            except Exception as e:
                print('cannot create file %s %s' % (abs_path, e))
                continue
            write_prev_li = True
            if parentdir == "/home/nwalsh/blog":
                write_prev_li = False
            index_file.write(f'''<!DOCTYPE html>
    <html>
     <head></head>
     <body>
      <div>
      <h1>{os.path.basename(os.path.abspath(parentdir))}</h1>
       <table cellspacing="15">
        <thead><tr><th>name</th><th>date</th><th>size</th></tr><thead>
        <tbody>
           {'<tr><td colspan="3"><a href="../index.html">..</a></td></tr>' if write_prev_li else ''}''')

        for dirname in sorted(dirs):
            if ".git" in dirname:
                continue

            absolute_dir_path = os.path.join(parentdir, dirname)

            if not os.access(absolute_dir_path, os.W_OK):
                print("***ERROR*** folder {} is not writable! SKIPPING!".format(absolute_dir_path))
                continue
            if opts.verbose:
                print('DIR:{}'.format(absolute_dir_path))

            if not opts.dryrun:
                index_file.write(f"""<tr><td colspan="3"><a href="{dirname}/index.html">{dirname + '/'}</a></td></tr>""")
            process_dir(absolute_dir_path, opts)

        files_by_time = []
        for filename in files:
            if opts.filter and not fnmatch.fnmatch(filename, opts.filter):
                if opts.verbose:
                    print('SKIP: {}/{}'.format(parentdir, filename))
                continue

            if opts.verbose:
                print('{}/{}'.format(parentdir, filename))

            # don't include index.html in the file listing
            if filename.strip().lower() == index_file_name.lower():
                continue

            try:
                time = os.path.getctime(os.path.join(parentdir, filename))
                size = int(os.path.getsize(os.path.join(parentdir, filename)))

                if not opts.dryrun:
                    dt = datetime.datetime.utcfromtimestamp(time)
                    entry = f"""<tr><td><a href="{filename}">{filename}</a></td><td>{dt.isoformat()}</td><td><span class="size">{pretty_size(size)}</span></td></tr>"""
                    files_by_time.append((dt, entry))
            except Exception as e:
                print('ERROR writing file name:', e)
                repr(filename)

        for _, entry in sorted(files_by_time, key=lambda x: x[0], reverse=True):
            index_file.write(entry)

        if not opts.dryrun:
            index_file.write("""
  </tbody></table>
  </div>
 </body>
</html>""")
            index_file.close()


# bytes pretty-printing
UNITS_MAPPING = [
    (1024 ** 5, ' PB'),
    (1024 ** 4, ' TB'),
    (1024 ** 3, ' GB'),
    (1024 ** 2, ' MB'),
    (1024 ** 1, ' KB'),
    (1024 ** 0, (' byte', ' bytes')),
]


def pretty_size(bytes, units=UNITS_MAPPING):
    """Human-readable file sizes.
    ripped from https://pypi.python.org/pypi/hurry.filesize/
    """
    for factor, suffix in units:
        if bytes >= factor:
            break
    amount = int(bytes / factor)

    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='''DESCRIPTION:
    Generate directory index files recursively.
    Start from current dir or from folder passed as first positional argument.
    Optionally filter by file types with --filter "*.py". ''')

    parser.add_argument('top_dir',
                        nargs='?',
                        action='store',
                        help='top folder from which to start generating indexes, '
                             'use current folder if not specified',
                        default=os.getcwd())

    parser.add_argument('--filter', '-f',
                        help='only include files matching glob',
                        required=False)

    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        help='***WARNING: this can take a very long time with complex file tree structures***'
                             ' verbosely list every processed file',
                        required=False)

    parser.add_argument('--dryrun', '-d',
                        action='store_true',
                        help="don't write any files, just simulate the traversal",
                        required=False)

    config = parser.parse_args(sys.argv[1:])

    process_dir(config.top_dir, config)
