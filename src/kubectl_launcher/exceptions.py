class KubectlLauncherInvalidConfig(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class KubectlLauncherAppException(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class KubectlLauncherYamlException(Exception):
    def __init__(self, message: str):
        super().__init__(message)