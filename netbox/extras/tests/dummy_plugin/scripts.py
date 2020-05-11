from extras.scripts import *


class PluginScript(Script):
    animal = StringVar()

    def run(self, data, commit):
        print(f"Raaar! I'm a(n) {data['animal']}")


scripts = [PluginScript]
