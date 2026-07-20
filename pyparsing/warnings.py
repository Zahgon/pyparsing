class PyparsingWarning(UserWarning):
    pass


class PyparsingDeprecationWarning(PyparsingWarning, DeprecationWarning):
    pass


class PyparsingDiagnosticWarning(PyparsingWarning):
    pass
