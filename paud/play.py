import tempfile


class Play:
    def __init__(self, env, data):
        self.env = env
        self.data = data

        self.available_env = {
            "termux": self.termux,
            "windows": self.windows,
            "linux": self.linux,
            "macos": self.macos,
        }

        self.available_env[self.env]()

    def termux(self):
        from subprocess import Popen, PIPE

        with tempfile.NamedTemporaryFile() as temp:
            temp.write(self.data)
            Popen(
                ("termux-media-player", "play", temp.name),
                stdout=PIPE,
                shell=False
            )

    def windows(self):
        import winsound

        winsound.PlaySound(self.data, winsound.SND_MEMORY | winsound.SND_NOSTOP)

    def linux(self):
        pass

    def macos(self):
        pass

    def pyaudio_play(self):
        pass
