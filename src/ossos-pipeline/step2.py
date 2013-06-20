#!/usr/bin/env python
'''run step2 of the OSSOS pipeline.'''

import os
import argparse
import logging
from ossos import util
from ossos import storage

def run_step2(expnums, ccd, version, prefix=None):
    '''run the actual step2  on the given exp/ccd combo'''

    jmp_args = ['step2jmp']
    matt_args = ['step2matt_jmp']

    idx = 0
    for expnum in expnums:
        jmp_args.append(
            storage.get_image(expnum,
                              ccd=ccd,
                              version=version,
                              ext='obj.jmp',
                              prefix=prefix
                              )[0:-8]
            )
        idx += 1
        matt_args.append('-f%d' % ( idx))
        matt_args.append(
            storage.get_image(expnum,
                              ccd=ccd,
                              version=version,
                              ext='obj.matt',
                              prefix=prefix
                              )[0:-9]
            )

    util.exec_prog(jmp_args)
    util.exec_prog(matt_args)

    for expnum in expnums:
        for ext in ['unid.jmp', 'unid.matt', 'trans.jmp']:
            uri = storage.dbimages_uri(expnum,ccd=ccd,version=version,ext=ext, prefix=prefix)
            filename = os.path.basename(uri)
            storage.copy(filename, uri)


    return

if __name__ == '__main__':
    ### Must be running as a script

    parser=argparse.ArgumentParser(
        description='Run step2jmp and step2matt on a given exposure.')

    parser.add_argument("--ccd","-c",
                        action="store",
                        default=None,
                        type=int,
                        dest="ccd")
    parser.add_argument("--fk", action="store_true", default=False, help="Do fakes?")
    parser.add_argument("--dbimages",
                        action="store",
                        default="vos:OSSOS/dbimages",
                        help='vospace dbimages containerNode')
    parser.add_argument("expnums",
                        type=int,
                        nargs=3,
                        help="3 expnums to process")
    parser.add_argument("--version",
                        action='version',
                        version='%(prog)s 1.0')
    parser.add_argument('-t','--type',
                        help='which type of image to process',
                        choices=['s','p','o'],
                        default='p'
                        )
    parser.add_argument('--no-sort',
                        help='preserve input exposure order',
                        action='store_true')
    parser.add_argument("--verbose","-v",
                        action="store_true")

    args=parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    storage._dbimages = args.dbimages

    if args.ccd is None:
        ccdlist = range(0,36)
    else:
        ccdlist = [args.ccd]

    prefix = ( args.fk and "fk") or ""

    if not args.no_sort:
        args.expnums.sort()

    for ccd in ccdlist:
        try:
            message = 'success'
            #if not storage.get_status(expnum, ccd, 'mkpsf'):
            #    raise IOError(35, "missing mkpsf")
            #if storage.get_status(expnum, ccd, 'step1'):
            #    logging.info("Already did %s %s, skipping" %(str(expnum),
            #                                                 str(ccd)))
            #    continue
            logging.info("step2 on expnum :%s, ccd: %d" % (
                str(args.expnums), ccd))
            run_step2(args.expnums, ccd, version=args.type, prefix=prefix)
            logging.info(message)
        except Exception as e:
            message = str(e)
            logging.error(message)

            #storage.set_status(expnum,
            #                   ccd,
            #                   'step2',
            #                   message)
        
            

