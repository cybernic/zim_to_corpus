#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extracts all Wikipedia HTMLs from the files output by zim_to_dir. Each
Wikipedia page is filtered and converted into a minimal HTML, and then saved
as a JSON string. In theory, this step could have been
skipped, and the script that creates the final format(s) could have operated on
the output of zim_to_dir. However, filtering substantially decreases the size
of, and access time to, the data. This factor becomes important, as there are
several output formats and the converter script might be called for all of them.
Finally, the JSON-per-line format is ubiquitous, while the output of zim_to_dir
is not.
"""

from argparse import ArgumentParser
import gzip
from io import StringIO
import json
import logging
from multiprocessing import Pool
import os
import os.path as op

from multiprocessing_logging import install_mp_handler

from zim_to_corpus.wiki import enumerate_static_dump, ZimHtmlParser


def parse_arguments():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', '-i', required=True,
                        help='the input directory.')
    parser.add_argument('--output-dir', '-o', required=True,
                        help='the output directory.')
    parser.add_argument('--processes', '-P', type=int, default=1,
                        help='number of worker processes to use (max is the '
                             'num of cores, default: 1)')
    parser.add_argument('--log-level', '-L', type=str, default='info',
                        choices=['debug', 'info', 'warning', 'error', 'critical'],
                        help='the logging level.')
    args = parser.parse_args()

    num_procs = len(os.sched_getaffinity(0))
    if args.processes < 1 or args.processes > num_procs:
        parser.error('Number of processes must be between 1 and {}'.format(
            num_procs))
    return args


def convert_to_json(input_file: str, output_file: str) -> int:
    """
    Parses all Wikipedia pages in _input_file_ and writes them to in a simple
    HTML format to _output_file_ as one JSON string per line.

    :returns: the number of documents converted.
    """
    logging.debug(f'Converting {input_file} to {output_file}...')
    try:
        with gzip.open(output_file, 'wt') as outf:
            for doc_no, html in enumerate(enumerate_static_dump(input_file), 1):
                wp = ZimHtmlParser.parse(html)
                print(json.dumps(wp.prettify()), file=outf)
    except EOFError as ee:
        logging.error(ee)
        return doc_no
    except:
        logging.exception(f'Error in {input_file}, document {doc_no}.')
        raise

    logging.debug(f'Converted {doc_no} documents from '
                  f'{input_file} to {output_file}.')
    return doc_no


def main():
    args = parse_arguments()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(process)s - %(levelname)s - %(message)s'
    )
    install_mp_handler()

    os.nice(20)
    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)

    in_out_files = [(op.join(args.input_dir, f), op.join(args.output_dir, f))
                    for f in os.listdir(args.input_dir)]

    logging.info(f'Scheduled {len(in_out_files)} files for conversion.')

    with Pool(args.processes) as pool:
        total_docs = sum(pool.starmap(convert_to_json, in_out_files))

    logging.info(f'Done. Converted a total of {total_docs} documents.')


if __name__ == '__main__':
    main()
