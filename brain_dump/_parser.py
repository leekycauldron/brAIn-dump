import whisper
import torch
import gc

class Transcriber:
    def __init__(self, model="large"):
        self._model = whisper.load_model(model)
        print("Transcriber loaded.")

    def transcribe(self, audio_file):
        return self._model.transcribe(audio_file)["text"]

    def close(self):
        del self._model
        torch.cuda.empty_cache()
        gc.collect()

if __name__ == "__main__":
    t = Transcriber()
    print(t.transcribe("output.wav"))
    t.close()