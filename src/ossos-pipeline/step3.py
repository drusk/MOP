#!/usr/bin/env python
'''run step3 of the OSSOS pipeline.'''

import os
import argparse
import logging
from ossos import util
from ossos import storage

def run_step3(expnums, ccd, version, rate_min,
              rate_max, angle, width, field=None, prefix=None):
    '''run the actual step2  on the given exp/ccd combo'''

    jmp_args = ['step3jmp']
    matt_args = ['step3matt']

    idx = 0
    cmd_args = []
    for expnum in expnums:
        idx += 1
        for ext in ['unid.jmp', 'unid.matt',
                    'trans.jmp' ]:
            filename = storage.get_image(expnum,
                                         ccd=ccd,
                                         version=version,
                                         ext=ext,
                                         prefix=prefix
                                         )
        image = os.path.splitext(os.path.splitext(os.path.basename(filename))[0])[0]
        cmd_args.append('-f%d' % ( idx))
        cmd_args.append(image)

    cmd_args.extend(['-rn', str(rate_min),
                     '-rx', str(rate_max),
                     '-a', str(angle),
                     '-w', str(width)])
    jmp_args.extend(cmd_args)
    matt_args.extend(cmd_args)
    util.exec_prog(jmp_args)
    util.exec_prog(matt_args)


    if field is None:
        field = str(expnums[0])
    storage.mkdir(os.path.dirname(
        storage.get_uri(field,
                        ccd=ccd,
                        version=version,
                        ext=ext,
                        prefix=prefix)))

    for ext in ['moving.jmp', 'moving.matt']:
        uri = storage.get_uri(field,
                              ccd=ccd,
                              version=version,
                              ext=ext,
                              prefix=prefix)
        filename = '%s%d%s%s.%s' % ( prefix, expnums[0],
                                   version,
                                   str(ccd).zfill(2),
                                   ext)
        storage.copy(filename, uri)


    return

if __name__ == '__main__':
    ### Must be running as a script

    parser=argparse.ArgumentParser(
        description='Run step3jmp and step3matt on a given triple.')

    parser.add_argument("--ccd","-c",
                        action="store",
                        default=None,
                        type=int,
                        dest="ccd")
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
    parser.add_argument('--fk', help='Do fakes?', default=False, action='store_true')
    parser.add_argument('--field',
                        help='a string that identifies which field is being searched',
                        nargs='?')
    parser.add_argument('--no-sort',
                        help='preserve input exposure order',
                        action='store_true')
    parser.add_argument("--verbose","-v",
                        action="store_true")
    parser.add_argument("--rate_min", default=0.4,
                        help='minimum rate to accept',
                        type=float)
    parser.add_argument('--rate_max', default=15,
                        help='maximum rate to accept',
                        type=float)
    parser.add_argument('--angle', default=20,
                        help='angle of x/y motion, West is 0, North 90',
                        type=float)
    parser.add_argument('--width', default=30,
                        help='openning angle of search cone',
                        type=float)

    args=parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    storage._dbimages = args.dbimages

    if args.ccd is None:
        ccdlist = range(0,36)
    else:
        ccdlist = [args.ccd]

    if not args.no_sort:
        args.expnums.sort()

    prefix = ( args.fk and 'fk') or ''

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
            run_step3(args.expnums, ccd, version=args.type,
                      rate_min=args.rate_min,
                      rate_max=args.rate_max,
                      angle=args.angle,
                      width=args.width,
                      field=args.field,
                      prefix=prefix)
            logging.info(message)
        except Exception as e:
            message = str(e)
            logging.error(message)

            #storage.set_status(expnum,
            #                   ccd,
            #                   'step2',
            #                   message)
        
            

