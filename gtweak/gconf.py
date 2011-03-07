import subprocess

from gi.repository import GConf

class GConfSetting:
    def __init__(self, key):
        self._key = key
        self._client = GConf.Client.get_default()
        self._cmd_cache = {}

    def _run_gconftool(self, command):
        if command not in self._cmd_cache:
            p = subprocess.Popen(["gconftool-2", command, self._key], stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
            stdout, stderr = p.communicate()
            if p.returncode == 0:
                self._cmd_cache[command] = stdout.strip()
            else:
                self._cmd_cache[command] = "ERROR: %s" % stderr.strip()
        return self._cmd_cache[command]

    def schema_get_summary(self):
        return self._run_gconftool("--short-docs")
        
    def schema_get_description(self):
        return self._run_gconftool("--long-docs").strip()

    def schema_get_all(self):
        return {"summary":self.schema_get_summary(), "description":self.schema_get_description()}

if __name__ == "__main__":
    key = "/apps/metacity/general/compositing_manager"
    s = GConfSetting(key)
    print s.schema_get_summary(), s.schema_get_description()
    print s.schema_get_all()
