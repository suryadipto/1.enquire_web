import enquire
import argparse


def _get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('tag', type=str, help='Specify tag')
    parser.add_argument('to_py', type=str, help='Specify path to text file')
    parser.add_argument('--thr', type=int, help='Specify threshold', default=1)
    parser.add_argument('--wd', type=str, help='Specify password', default='$(pwd)/')
    parser.add_argument('comb', type=int, help='specify comb', default=4)
    parser.add_argument('--A', type=int, help='specify A', default=2)
    parser.add_argument('--K', type=int, help='specify K', default=3)
    parser.add_argument('--etype', type=int, help='specify etype', default='all')
    parser.add_argument('--rscript', type=str, help='specify rscript path', default='rscript_path')
    parser.add_argument('--ncores', type=int, help='specify ncores', default=32)
    return parser


if __name__ == '__main__':
    args = _get_parser().parse_args()
    _, _ = enquire.run(args.tag, args.to_py, args.thr, args.wd, args.comb, args.A, args.K, args.etype, args.rscript, args.ncores)
    