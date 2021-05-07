import logging
import sys
from kubectl_launcher.kubectl import KubectlLauncher
from kubectl_launcher.report import Reporter
from kubectl_launcher.api import InitData
from kubectl_launcher.exceptions import KubectlLauncherAppException
from kubectl_launcher.config import Config

log = logging.getLogger(__name__)


def main():
    try:
        data = InitData.init()
        if data.should_run():
            config = Config(data.args['config'])
            kubelauncher = KubectlLauncher(config,data)
            kubelauncher.run()
            results = kubelauncher.all_results
        if data.should_run() and data.should_generate_report():
            Reporter(data,results).generate()
    except KubectlLauncherAppException as e:
        log.error(e)
        sys.exit(1)
    except Exception as e:
        print(e)
        log.exception('Fatal error')
        sys.exit(2)

if __name__ == '__main__':
    main()
