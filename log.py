from blessings import Terminal


class Logger(object):

    def __init__(self, t=Terminal()):
        self.t = t

    def info(self, msg):
        print(self.t.green(str(msg)))

    def warn(self, msg):
        print(self.t.yellow(str(msg)))

    def err(self, msg):
        print(self.t.red(str(msg)))

    def fmt(self, msg):
        print(str(msg).format(t=self.t))
