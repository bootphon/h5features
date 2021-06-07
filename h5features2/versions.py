from pyh5features import Writer as pywriter
class Versions:
    """ This class allow to return the different version of writing """
    def versions():
        """ Return a list of version available
        Returns:
            list: list of `str` containing available versions

        """
        versions = {
            "v1_0" : "1.0",
            "v1_1" : "1.1",
            "v1_2" : "1.2",
            "v2_0" : "2.0",
        }
        return [versions[key] for key in pywriter.version.__members__.keys()]