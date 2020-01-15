import argparse
from glob import glob
from pathlib import Path
from typing import Any, Dict, Union, TypeVar

PathIsh = Union[str, Path]
Json = Dict[str, Any] # TODO Mapping?


T = TypeVar('T')
Res = Union[T, Exception]


def make_parser(single_source=False):
    p = argparse.ArgumentParser(
        'DAL (Data Access/Abstraction Layer)',
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=100), # type: ignore
    )
    source_help = 'Path to exported data'
    if not single_source:
        source_help += ". Can be single file, or a glob, e.g. '/path/to/exports/*.ext'"

    p.add_argument(
        '--source',
        type=str,
        required=True,
        help=source_help,
    )
    # TODO link to exports post why multiple exports could be useful
    if not single_source:
        p.add_argument(
            '--no-glob',
            action='store_true',
            help='Treat path in --source literally'
        )
    p.add_argument('-i', '--interactive', action='store_true', help='Start Ipython session to play with data')

    p.epilog = """
You can use =dal.py= (stands for "Data Access/Abstraction Layer") to access your exported data, even offline.
I elaborate on motivation behind it [[https://beepb00p.xyz/exports.html#dal][here]].

- main usecase is to be imported as python module to allow for *programmatic access* to your data.

  You can find some inspiration in [[https://beepb00p.xyz/mypkg.html][=my.=]] package that I'm using as an API to all my personal data.

- to test it against your export, simply run: ~./dal.py --source /path/to/export~

- you can also try it interactively: ~./dal.py --source /path/to/export --interactive~

"""
    return p


def main(*, DAL, demo=None, single_source=False):
    """
    single_source: used when exports are not cumulative/synthetic
    (you can find out more about it here: https://beepb00p.xyz/exports.html#types)
    """
    p = make_parser(single_source=single_source)
    args = p.parse_args()

    if single_source:
        dal = DAL(args.source)
    else:
        if '*' in args.source and not args.no_glob:
            sources = glob(args.source)
        else:
            sources = [args.source]
        dal = DAL(sources)
    # logger.debug('using %s', sources)

    print(dal)
    # TODO autoreload would be nice... https://github.com/ipython/ipython/issues/1144
    # TODO maybe just launch through ipython in the first place?
    if args.interactive:
        import IPython # type: ignore
        IPython.embed(header="Feel free to mess with 'dal' object in the interactive shell")
    else:
        assert demo is not None, "No 'demo' in 'dal.py'?"
        demo(dal)


def logger(logger, **kwargs):
    # TODO FIXME vendorize
    try:
        # pylint: disable=import-error
        from kython.klogging import LazyLogger # type: ignore
    except ModuleNotFoundError as ie:
        import logging
        logging.exception(ie)
        logging.warning('fallback to default logger!')
        return logging.getLogger(logger)
    else:
        return LazyLogger(logger, **kwargs)


__all__ = [
    'PathIsh',
    'Json',
    'Res',
]

