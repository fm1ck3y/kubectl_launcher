import logging
import os
from jinja2 import Environment, PackageLoader, select_autoescape
from kubectl_launcher.api import InitData
import kubectl_launcher
log = logging.getLogger(__name__)



class Reporter:
    TEMPLATES_DIR = 'templates'

    def __init__(self, data: InitData,results: dict):
        self.html_report_file = os.path.join(data.args['output'], data.args['html_report'])
        environment = Environment(
            loader=PackageLoader(kubectl_launcher.__name__, self.TEMPLATES_DIR),
            autoescape=select_autoescape(['html']),
        )
        self.template = environment.get_template('report.html')
        self.results = results

    def generate(self):
        log.info('Start report generation')
        html_report = self.template.render(results = self.results)
        self._dump(html_report)
        log.info('Finish report generation')

    def _dump(self, html_report: str):
        with open(self.html_report_file, 'w') as f:
            f.write(html_report)
