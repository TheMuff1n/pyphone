from pyVoIP.VoIP import VoIPPhone, InvalidStateError, CallState
import wave
import time
import os
import tempfile

def answer(call):
    print("A call!")
    try:
        with wave.open("sample.wav", "rb") as f:
            frames = f.getnframes()
            data = f.readframes(frames)

        call.answer()

        call.write_audio(data)
        stop = time.time() + (frames / 8000)
        while time.time() <= stop and call.state == CallState.ANSWERED:
            time.sleep(0.1)

        stop = time.time() + 100 # maximum call time of 10 seconds

        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as temp_file:
            temp_filename = temp_file.name
            while time.time() <= stop and call.state == CallState.ANSWERED:
                data = call.read_audio(length=160, blocking=False)
                
                last_index = len(data) - 1
                while last_index >= 0 and data[last_index] == 0x80:
                    last_index -= 1
                
                without_trailing_80 = data[:last_index + 1]

                temp_file.write(without_trailing_80)
                time.sleep(0.01)

        # hang up if the call is still active
        if call.state == CallState.ANSWERED:
            call.hangup()

        with open(temp_filename, "rb") as temp_file:
            data = temp_file.read()

        with wave.open("output.wav", "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(1)
            wav_file.setframerate(8000)
            wav_file.writeframes(data)

        os.remove(temp_filename)

    except InvalidStateError:
        pass

if __name__ == "__main__":
    phone=VoIPPhone("192.168.178.1", 5060, "voip-test", "daspatentabc", callCallback=answer, myIP="192.168.178.38")
    phone.start()
    input("Press enter to disable the phone")
    phone.stop()
