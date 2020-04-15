class LoopDetected(Exception):
    """
    A loop has been detected while tracing a cable path.
    """
    pass


class CableTraceSplit(Exception):
    """
    A cable trace cannot be completed because a RearPort maps to multiple FrontPorts and
    we don't know which one to follow.
    """
    def __init__(self, termination, *args, **kwargs):
        self.termination = termination
