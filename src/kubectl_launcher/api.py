import logging
import argparse
import os
from kubectl_launcher import __version__ as version
import datetime


log = logging.getLogger(__name__)


class InitData:
    def __init__(self, args):
        self.args = args

    def should_run(self):
        return self.args['subparser'] == 'run'

    def should_generate_report(self):
        return self.args['subparser'] == 'report' or (self.args['subparser'] == 'run' and self.args['report'])


    @staticmethod
    def __init_logger(debug: bool):
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
        logging.getLogger("kubernetes").setLevel(logging.INFO)
        logging.getLogger("urllib3").setLevel(logging.INFO)
        logging.getLogger("urllib3").propagate = False

    @classmethod
    def init(cls):
        args = cls.__parse_args()
        cls.__init_logger(args.args['debug'])
        now = datetime.datetime.now()
        args.args['html_report'] = f'kubectl_launcher_report_{now}.html'
        cls.__create_dirs([args.args['output']])
        return args

    @staticmethod
    def __create_dirs(dirs: list):
        for dir in dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)
                logging.debug(f"Directory {dir} successfull create.")
            else:
                logging.debug(f"Directory {dir} already exist.")

    @classmethod
    def __parse_args(cls):
        parser = argparse.ArgumentParser(prog='kubectl')
        parser.add_argument('--debug', action='store_true',
                            help='When debug mode turn on, in logging send debug messages.')
        parser.add_argument('--version',action='version', version='%(prog)s {}'.format(version))
        parser.add_argument('-o', '--output', default='reports', help='Directory for reports')
        subparsers = parser.add_subparsers(dest='subparser', required=True)

        run_deployment = subparsers.add_parser('run', help='run deployment')
        run_deployment.add_argument('--config', '-c', default='config',
                                    type=argparse.FileType('r'), help='Run deployment with config file')

        run_deployment.add_argument('-r', '--report', action='store_true', help='Generate report after kinds run')
        #args = ['--debug', 'run', '-yc', 'kubectl_example_config.yaml','-r']
        return cls(vars(parser.parse_args()))
