import queue
import asyncio
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from helper import is_demo_intent,narrate_step
from run_demo import run



 # Audio queues
mic_q: "queue.Queue[bytes]" = queue.Queue(maxsize=300)
spk_q: "queue.Queue[bytes]" = queue.Queue(maxsize=300)
playback_buf = bytearray()



# State for tracking transcripts
# State for tracking
STATE = {
    "latest_transcript": "",
    "is_speaking": False,  # Track if AI is speaking
    "mute_mic": False      # Flag to mute microphone
}
latest_transcript_event = asyncio.Event()


def mic_cb(indata, frames, time_info, status):
        # SOLUTION 1: Mute mic while AI is speaking
        if STATE["is_speaking"] or STATE["mute_mic"]:
            return  # Don't send any audio
            
        data = bytes(indata)
        try:
            mic_q.put_nowait(data)
        except queue.Full:
            pass

def spk_cb(outdata, frames, time_info, status):
    mv = memoryview(outdata)
    need = len(mv)

    while len(playback_buf) < need:
        try:
            playback_buf.extend(spk_q.get_nowait())
        except queue.Empty:
            break

    n = min(need, len(playback_buf))
    if n:
        mv[:n] = playback_buf[:n]
        del playback_buf[:n]

    if n < need:
        mv[n:need] = b"\x00" * (need - n)

# Async tasks
async def send_mic_audio(session):
    while True:
        chunk = await asyncio.to_thread(mic_q.get)
        if not STATE["is_speaking"]:
            try:

                await session.send_audio(chunk)
                # print("audio chunk sent")
            except (ConnectionClosedOK, ConnectionClosedError, asyncio.CancelledError):
                print("send_mic_audio: session closed, stopping send loop")
                break
            except Exception as e:
                print("send_mic_audio: unexpected send error:", e)
                break


async def monitor_playback():
    last_check = 0
    while True:
        await asyncio.sleep(0.1)
        current = len(playback_buf)
        
        # If buffer was emptying and now empty, AI finished speaking
        if last_check > 0 and current == 0 and STATE["is_speaking"]:
            await asyncio.sleep(0.3)  # Grace period
            if len(playback_buf) == 0:  # Still empty
                STATE["is_speaking"] = False
                print("Mic re-enabled")
        
        last_check = current