# user_text="shows me the demo"
# ls=user_text.split()
# print("list of words",ls)

# def is_demo_intent(text: str) -> bool:
#     keywords = [
#         "show",
#         "demo",
#         "demonstrate",
#         "product",
#         "application"
#     ]
#     text = text.lower()
#     return any(k in text for k in keywords)

# print("result:",is_demo_intent(user_text))


# async def capture_frame_from_rtp(host: str, port: int, timeout: float = 3.0) -> 'rtc.VideoFrame':
#     """Capture a single frame from an RTP stream using ffmpeg and return an rtc.VideoFrame.

#     Requires `ffmpeg` available on PATH. This runs `ffmpeg` as a subprocess
#     and reads one frame as PNG from stdout.
#     """
#     # Build a minimal SDP describing the incoming RTP H264 stream (payload type 96).
#     # ffmpeg needs an SDP to map dynamic payload types (e.g. 96) to codecs.
#     sdp = (
#         f"v=0\n"
#         f"o=- 0 0 IN IP4 {host}\n"
#         f"s=No Name\n"
#         f"c=IN IP4 {host}\n"
#         f"t=0 0\n"
#         f"m=video {port} RTP/AVP 96\n"
#         f"a=rtpmap:96 H264/90000\n"
#     )

#     # Write SDP to a temp file and instruct ffmpeg to read it as input.
#     with tempfile.NamedTemporaryFile("w", suffix=".sdp", delete=False) as tf:
#         tf.write(sdp)
#         sdp_path = tf.name

#     cmd = [
#         "ffmpeg",
#         "-nostdin",
#         "-protocol_whitelist",
#         "file,udp,rtp",
#         "-i",
#         sdp_path,
#         "-frames:v",
#         "1",
#         "-f",
#         "image2pipe",
#         "-vcodec",
#         "png",
#         "-",
#     ]

#     last_err = None
#     attempts = 3
#     try:
#         for attempt in range(1, attempts + 1):
#             proc = await _asyncio.create_subprocess_exec(
#                 *cmd, stdout=_asyncio.subprocess.PIPE, stderr=_asyncio.subprocess.PIPE
#             )
#             try:
#                 # Use a longer timeout for RTP arrival; increase per attempt
#                 cur_timeout = timeout * (2 if attempt > 1 else 1)
#                 stdout, stderr = await _asyncio.wait_for(proc.communicate(), timeout=cur_timeout)
#             except _asyncio.TimeoutError:
#                 proc.kill()
#                 await proc.wait()
#                 last_err = b"timeout"
#                 if attempt < attempts:
#                     await _asyncio.sleep(0.5)
#                     continue
#                 raise TimeoutError("ffmpeg timed out waiting for RTP packets")

#             last_err = stderr
#             if proc.returncode != 0 and not stdout:
#                 # ffmpeg failed immediately (e.g., unsupported input)
#                 if attempt < attempts:
#                     await _asyncio.sleep(0.5)
#                     continue
#                 raise RuntimeError(f"ffmpeg failed: {stderr.decode(errors='ignore')}")

#             # Got image data
#             img = Image.open(io.BytesIO(stdout)).convert("RGB")
#             w, h = img.size
#             buf = img.tobytes()
#             vf = rtc.VideoFrame(w, h, rtc.VideoBufferType.RGB24, buf)
#             return vf
#     finally:
#         try:
#             os.remove(sdp_path)
#         except Exception:
#             pass

#     # If we exit loop without returning, surface last stderr
#     raise RuntimeError(f"ffmpeg failed after {attempts} attempts: {last_err.decode(errors='ignore') if isinstance(last_err, (bytes, bytearray)) else last_err}")





# async def publish_screen_sharess():
#         """Stream a Playwright `page` to LiveKit as a video track.

#         If `page` is None the function will launch Playwright headless and open
#         `target_url` (if provided). It publishes a LocalVideoTrack backed by a
#         `rtc.VideoSource` and repeatedly captures screenshots at `fps`.

#         Cleanup: unpublishes the track and closes any browser/playwright started
#         by this function.
#         """
#         await start_server()
#         started_playwright = False
#         playwright = None
#         browser = None
#         fps: int = 8
#         max_width: int | None = None

#         # If caller passed a page, use it. Otherwise start a headless page.
        
#         playwright = await async_playwright().start()
#         browser = await playwright.chromium.launch(headless=True,slow_mo=10000)
#         context = await browser.new_context(viewport={"width": 1280, "height": 720})
#         page = await context.new_page()
        
#         await page.goto(ONCREATE_URL, wait_until="domcontentloaded")
#         await voice_generation(text="Hey, I am Oncreate's Demo agent so how can I help you today!")
#         # await page.get_by_role("button", name="+ New Agent").click()
#         async def receive_and_play(session):
#             demo_started=False
#             try:
#                 async for event in session:
#                     if event.type == "audio":
#                         # Mark that AI is speaking when audio starts
#                         STATE["is_speaking"] = True
#                         try:
#                             spk_q.put_nowait(event.audio.data)
#                         except queue.Full:
#                             pass

#                     elif event.type == "raw_model_event":
#                         t = getattr(event.data, "type", None)
                        
#                         # SOLUTION 2: Track when response starts and ends
#                         if t == "response.audio.delta":
#                             STATE["is_speaking"] = False
                            
#                         elif t == "response.audio.done" or t == "response.done":
#                             STATE["is_speaking"] = False
#                             # Add small delay to ensure playback finished
#                             await asyncio.sleep(0.5)
                        
#                         elif t == "input_audio_transcription_completed":
#                             user_text = (getattr(event.data, "transcript", "") or "").strip()
#                             STATE["is_speaking"]=False
                            
#                             # SOLUTION 3: Ignore transcripts while AI is speaking
#                             if  STATE["is_speaking"]:
#                                 print(f"[Ignored feedback]: {user_text}")
#                                 continue
                            
#                             STATE["latest_transcript"] = user_text
#                             latest_transcript_event.set()
                            
#                             if user_text:
#                                 print("User:", user_text)
                                
#                                 # Check for demo intent
#                                 if not demo_started and is_demo_intent(user_text):
#                                     demo_started = True
#                                     STATE["mute_mic"] = True  # Mute during demo
#                                     print("Starting demo...")
                                    
#                                     async def on_step(step):
#                                         await narrate_step(step)
#                                         print(f"Demo step: {step}")
                                    
#                                     asyncio.create_task(run(on_step,page=page,browser=browser))

#                     elif event.type == "error":
#                         print("Realtime error:", getattr(event, "error", event))
#                         break
#             except KeyboardInterrupt:
#                 print("Interrupt during voice process")


#         # Connect to LiveKit
#         room_obj = rtc.Room()
#         token = create_token(ROOM_NAME, "Demo-Agent")
#         await room_obj.connect(LIVEKIT_URL, token)
#         print("✅ Connected to LiveKit room")

#         # Allow page to paint
#         await asyncio.sleep(0.5)

#         # First screenshot to determine size
#         png = await page.screenshot(type="png")
#         img = Image.open(io.BytesIO(png)).convert("RGB")
#         width, height = img.size

#         # Create video source and local track once
#         video_src = rtc.VideoSource(width, height)
#         local_track = rtc.LocalVideoTrack.create_video_track("screen-share", video_src)
#         await room_obj.local_participant.publish_track(local_track)
#         print(f"✅ Published local video track (resolution={width}x{height})")

#         frame_interval = 1.0 / max(1, int(fps))

#         try:
#             while True:
#                 # start = time.time()
#                 # png = await page.screenshot(type="png")
#                 # img = Image.open(io.BytesIO(png)).convert("RGB")
#                 # if img.size != (width, height):
#                 #     img = img.resize((width, height), Image.BILINEAR)

#                 # buf = img.tobytes()
#                 # vf = rtc.VideoFrame(width, height, rtc.VideoBufferType.RGB24, buf)
#                 # timestamp_us = int(time.time() * 1_000_000)
#                 # video_src.capture_frame(vf, timestamp_us=timestamp_us)

#                 # elapsed = time.time() - start
#                 # await asyncio.sleep(max(0, frame_interval - elapsed))
#                 # Capture a single frame from an RTP stream (ffmpeg) and inject
#                 # it into the LiveKit VideoSource. The rtc.VideoSource class
#                 # doesn't provide a helper for RTP, so we use ffmpeg to grab
#                 # one frame and convert it to an rtc.VideoFrame.
#                 try:
#                     vf = await capture_frame_from_rtp("127.0.0.1", 5004)
#                 except (TimeoutError, RuntimeError) as e:
#                     print(f"RTP capture failed ({e}). Falling back to screenshot.")
#                     # Fallback: take a Playwright screenshot and convert to VideoFrame
#                     png = await page.screenshot(type="png")
#                     img = Image.open(io.BytesIO(png)).convert("RGB")
#                     if img.size != (width, height):
#                         img = img.resize((width, height), Image.BILINEAR)
#                     buf = img.tobytes()
#                     vf = rtc.VideoFrame(width, height, rtc.VideoBufferType.RGB24, buf)

#                 timestamp_us = int(time.time() * 1_000_000)
#                 video_src.capture_frame(vf, timestamp_us=timestamp_us)

#                 async with await runner.run() as session:
#                         print("🎙️ Voice assistant ready. Speak now...")
                        

#                         with sd.RawInputStream(
#                             samplerate=SAMPLE_RATE,
#                             channels=CHANNEL,
#                             dtype="int16",
#                             blocksize=BLOCK,
#                             callback=mic_cb,
#                         ), sd.RawOutputStream(
#                             samplerate=SAMPLE_RATE,
#                             channels=CHANNEL,
#                             dtype="int16",
#                             blocksize=BLOCK,
#                             callback=spk_cb,
#                         ):
#                             await asyncio.gather(
#                                 send_mic_audio(session),
#                                 receive_and_play(session),
#                                 monitor_playback()
                                
#                             )



#         except asyncio.CancelledError:
#             print("Screen share task cancelled, cleaning up...")
#         finally:
#             # Unpublish local track
#             try:
#                 await room_obj.local_participant.unpublish_track(local_track.sid)
#             except Exception:
#                 pass

#             # Close browser/playwright only if we started them here
#             if started_playwright:
#                 try:
#                     await browser.close()
#                 except Exception:
#                     pass
#                 try:
#                     await playwright.stop()
#                 except Exception:
#                     pass



# from voice_process import speak
# import json
# import websockets
# from config import OPENAI_WS,HEADERS
# import asyncio


# ws = websockets.connect(OPENAI_WS,additional_headers=HEADERS,ping_interval=10,ping_timeout=30,max_size=2**24)

# async def test_speak():
#     await speak(text="Hello there, how can I assist you today?")

# if __name__ == "__main__":
#     asyncio.run(test_speak())






# async def publish_screen_share_direct():
#     """
#     Direct approach: Use LiveKit VideoSource with WHIP ingress for better quality
#     This bypasses FFmpeg and uses LiveKit's native video handling
#     """
    
#     await start_server()
    
#     playwright = None
#     browser = None
#     room_obj = None
    
#     try:
#         # Launch Playwright
#         playwright = await async_playwright().start()
#         browser = await playwright.chromium.launch(
#             headless=True,
#             slow_mo=5000,
#             args=[
#                 '--disable-gpu',
#                 '--disable-dev-shm-usage',
#                 '--disable-setuid-sandbox',
#                 '--no-sandbox',
#             ]
#         )
#         context = await browser.new_context()
#         page = await context.new_page()
        
#         print(" Navigating to demo page...")
#         await page.goto(ONCREATE_URL, wait_until="domcontentloaded")

#         await inject_cursor_styles(page)
#         await set_cursor_mode(page,mode="arrow")

#         await click_with_cursor(page, 'button[data-title="Agents"]')
        
#         # ws= await connect_ws()
#         # Initial greeting
#         # await speak(ws,text="Hey, I am Oncreate's Demo agent so how can I help you today!")
        
#         tts= RealtimeTTS()

#         # await tts.connect()
#         # await tts.speak("Hey, I am Oncreate's Demo agent so how can I help you today!")
#         # await tts.close()
#         # Connect directly to LiveKit room (better than ingress for this use case)
#         print(" Connecting to LiveKit room...")
#         room_obj = rtc.Room()
        
#         # from config import LIVEKIT_API_KEY, LIVEKIT_API_SECRET
#         token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
#         token.with_identity("Demo-Agent")
#         token.with_name("Demo Agent")
#         token.with_grants(api.VideoGrants(
#             room_join=True,
#             room=ROOM_NAME,
#             can_publish=True,
#             can_subscribe=True,
#         ))
#         jwt_token = token.to_jwt()
        
#         await room_obj.connect(LIVEKIT_URL, jwt_token)
#         print(" Connected to LiveKit room")
        
#         # Wait for page to render
#         await asyncio.sleep(1)
        
#         # Capture first frame to get dimensions
#         png = await page.screenshot(type='png',timeout=60000)  # PNG doesn't support quality param
#         img = Image.open(io.BytesIO(png)).convert('RGB')
#         width, height = img.size
        
#         print(f" Video dimensions: {width}x{height}")
        
#         # Create LiveKit video source with higher quality
#         video_src = rtc.VideoSource(width, height)
#         local_track = rtc.LocalVideoTrack.create_video_track(
#             "screen-share",
#             video_src
#         )
        
#         # Publish with higher quality settings
#         await room_obj.local_participant.publish_track(
#             local_track,
#             rtc.TrackPublishOptions(
#                 source=rtc.TrackSource.SOURCE_SCREENSHARE,
#                 video_encoding=rtc.VideoEncoding(
#                     max_bitrate=3_000_000,  # 3 Mbps
#                     max_framerate=15.0,
#                 )
#             )
#         )
#         print(" Published high-quality video track")
        
#         # Voice interaction handler
#         async def receive_and_play(session):
#             demo_started = False
#             try:
#                 async for event in session:
#                     if event.type == "audio":
#                         STATE["is_speaking"] = True
#                         try:
#                             spk_q.put_nowait(event.audio.data)
#                         except queue.Full:
#                             pass
                    
#                     elif event.type == "raw_model_event":
#                         t = getattr(event.data, "type", None)
                        
#                         if t == "response.audio.delta":
#                             STATE["is_speaking"] = False
                        
#                         elif t == "response.audio.done" or t == "response.done":
#                             STATE["is_speaking"] = False
#                             await asyncio.sleep(0.5)
                        
#                         elif t == "input_audio_transcription_completed":
#                             user_text = (getattr(event.data, "transcript", "") or "").strip()
#                             STATE["is_speaking"] = False
                            
#                             if STATE["is_speaking"]:
#                                 print(f"[Ignored feedback]: {user_text}")
#                                 continue
                            
#                             STATE["latest_transcript"] = user_text
#                             latest_transcript_event.set()
                            
#                             if user_text:
#                                 print("User:", user_text)
                                
#                                 if not demo_started and is_demo_intent(user_text):
#                                     demo_started = True
#                                     STATE["mute_mic"] = True
#                                     print("Starting demo...")
#                                     await session.close()
                                    
#                                     # async def on_step(step):
#                                     #     await narrate_with_ws(step)
#                                     #     print(f"Demo step: {step}")
                                    
#                                     asyncio.create_task(run(page=page, browser=browser))
                    
#                     elif event.type == "error":
#                         print("Realtime error:", getattr(event, "error", event))
#                         break
                        
#             except KeyboardInterrupt:
#                 print("Interrupt during voice process")
        
#         # Screen capture loop
#         async def capture_and_publish():
#             fps = 15  # Higher FPS for smoother video
#             frame_interval = 1.0 / fps
#             frame_count = 0
            
#             try:
#                 while True:
#                     start = time.time()
                    
#                     # Capture high-quality screenshot
#                     png = await page.screenshot(type='png',timeout=30000)  # PNG is lossless, no quality param needed
#                     img = Image.open(io.BytesIO(png)).convert('RGB')
                    
#                     # Handle dimension changes
#                     w, h = img.size
#                     if (w, h) != (width, height):
#                         print(f" Dimension changed to {w}x{h}, recreating source...")
#                         # Would need to recreate video source here
#                         img = img.resize((width, height), Image.BILINEAR)
                    
#                     # Create VideoFrame and publish
#                     buf = img.tobytes()
#                     vf = rtc.VideoFrame(width, height, rtc.VideoBufferType.RGB24, buf)
#                     timestamp_us = int(time.time() * 1_000_000)
#                     video_src.capture_frame(vf, timestamp_us=timestamp_us)
                    
#                     frame_count += 1
#                     if frame_count % (fps * 5) == 0:
#                         print(f"📊 Published {frame_count} frames")
                    
#                     # Maintain frame rate
#                     elapsed = time.time() - start
#                     await asyncio.sleep(max(0, frame_interval - elapsed))
                    
#             except asyncio.CancelledError:
#                 print(" Stopping screen capture...")
#         # try:
#         #     asyncio.create_task(capture_and_publish())
#         # except Exception as e:
#         #     print(f"Error in screen capturing: {e}")
#         #     import traceback
#         #     traceback.print_exc()


        
#         # Start voice session and screen capture in parallel
#         print("🎙️ Starting voice assistant and screen capture...")
#         while True:
#             async with await runner.run() as session:
#                 print("🎙️ Voice assistant ready. Speak now...")
                
#                 with sd.RawInputStream(
#                     samplerate=SAMPLE_RATE,
#                     channels=CHANNEL,
#                     dtype="int16",
#                     blocksize=BLOCK,
#                     callback=mic_cb,
#                 ), sd.RawOutputStream(
#                     samplerate=SAMPLE_RATE,
#                     channels=CHANNEL,
#                     dtype="int16",
#                     blocksize=BLOCK,
#                     callback=spk_cb,
#                 ):
                    
#                     await asyncio.gather(
#                         send_mic_audio(session),
#                         receive_and_play(session),
#                         monitor_playback(),
#                         capture_and_publish()# Run screen capture in parallel
#                     )
    
#     except asyncio.CancelledError:
#         print("Screen share task cancelled...")
    
#     except Exception as e:
#         print(f"Error in publish_screen_sharess: {e}")
#         import traceback
#         traceback.print_exc()
#         raise
    
#     finally:
#         # Cleanup
#         print(" Cleaning up...")
        
#         if room_obj:
#             try:
#                 await room_obj.disconnect()
#             except Exception:
#                 pass
        
#         if browser:
#             try:
#                 await browser.close()
#             except Exception:
#                 pass
        
#         if playwright:
#             try:
#                 await playwright.stop()
#             except Exception:
#                 pass
        
#         print("Cleanup complete")


#NEW PUBLISH_SCREEN_SHARE_DIRECT


# async def publish_screen_share_direct():
#     """
#     Direct approach: Use LiveKit VideoSource with WHIP ingress for better quality
#     This bypasses FFmpeg and uses LiveKit's native video handling
#     """
    
#     await start_server()
    
#     playwright = None
#     browser = None
#     room_obj = None
    
#     try:
#         # Launch Playwright
#         playwright = await async_playwright().start()
#         browser = await playwright.chromium.launch(
#             headless=True,
#             slow_mo=5000,
#             args=[
#                 '--disable-gpu',
#                 '--disable-dev-shm-usage',
#                 '--disable-setuid-sandbox',
#                 '--no-sandbox',
#             ]
#         )
#         context = await browser.new_context()
#         page = await context.new_page()
        
#         print(" Navigating to demo page...")
#         await page.goto(ONCREATE_URL, wait_until="domcontentloaded")

#         await inject_cursor_styles(page)
#         await set_cursor_mode(page,mode="pointer")
#         await click_with_cursor(page, 'button[data-title="Agents"]')
        
#         # ws= await connect_ws()
#         # Initial greeting
#         # await speak(ws,text="Hey, I am Oncreate's Demo agent so how can I help you today!")
        
#         tts= RealtimeTTS()

#         # await tts.connect()
#         # await tts.speak("Hey, I am Oncreate's Demo agent so how can I help you today!")
#         # await tts.close()
#         # Connect directly to LiveKit room (better than ingress for this use case)
#         print(" Connecting to LiveKit room...")
#         room_obj = rtc.Room()
        
#         # from config import LIVEKIT_API_KEY, LIVEKIT_API_SECRET
#         token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
#         token.with_identity("Demo-Agent")
#         token.with_name("Demo Agent")
#         token.with_grants(api.VideoGrants(
#             room_join=True,
#             room=ROOM_NAME,
#             can_publish=True,
#             can_subscribe=True,
#         ))
#         jwt_token = token.to_jwt()
        
#         await room_obj.connect(LIVEKIT_URL, jwt_token)
#         print(" Connected to LiveKit room")
        
#         # Wait for page to render
#         await asyncio.sleep(1)
        
#         # Capture first frame to get dimensions
#         png = await page.screenshot(type='png',timeout=60000)  # PNG doesn't support quality param
#         img = Image.open(io.BytesIO(png)).convert('RGB')
#         width, height = img.size
        
#         print(f" Video dimensions: {width}x{height}")
        
#         # Create LiveKit video source with higher quality
#         video_src = rtc.VideoSource(width, height)
#         local_track = rtc.LocalVideoTrack.create_video_track(
#             "screen-share",
#             video_src
#         )
        
#         # Publish with higher quality settings
#         await room_obj.local_participant.publish_track(
#             local_track,
#             rtc.TrackPublishOptions(
#                 source=rtc.TrackSource.SOURCE_SCREENSHARE,
#                 video_encoding=rtc.VideoEncoding(
#                     max_bitrate=3_000_000,  # 3 Mbps
#                     max_framerate=15.0,
#                 )
#             )
#         )
#         print(" Published high-quality video track")
        
#         # Voice interaction handler
#         async def receive_and_play(session):
#             demo_started = False
#             try:
#                 async for event in session:
#                     if event.type == "audio":
#                         STATE["is_speaking"] = True
#                         try:
#                             spk_q.put_nowait(event.audio.data)
#                         except queue.Full:
#                             pass
                    
#                     elif event.type == "raw_model_event":
#                         t = getattr(event.data, "type", None)
                        
#                         if t == "response.audio.delta":
#                             STATE["is_speaking"] = False
                        
#                         elif t == "response.audio.done" or t == "response.done":
#                             STATE["is_speaking"] = False
#                             await asyncio.sleep(0.5)
                        
#                         elif t == "input_audio_transcription_completed":
#                             user_text = (getattr(event.data, "transcript", "") or "").strip()
#                             STATE["is_speaking"] = False
                            
#                             if STATE["is_speaking"]:
#                                 print(f"[Ignored feedback]: {user_text}")
#                                 continue
                            
#                             STATE["latest_transcript"] = user_text
#                             latest_transcript_event.set()
                            
#                             if user_text:
#                                 print("User:", user_text)
                                
#                                 if not demo_started and is_demo_intent(user_text):
#                                     demo_started = True
#                                     STATE["mute_mic"] = True
#                                     print("Starting demo...")
#                                     await session.close()
                                    
#                                     # async def on_step(step):
#                                     #     await narrate_with_ws(step)
#                                     #     print(f"Demo step: {step}")
                                    
#                                     asyncio.create_task(run_the_demo(page=page, browser=browser))
                    
#                     elif event.type == "error":
#                         print("Realtime error:", getattr(event, "error", event))
#                         break
                        
#             except KeyboardInterrupt:
#                 print("Interrupt during voice process")
        
#         # Screen capture loop
#         async def capture_and_publish():
#             fps = 15  # Higher FPS for smoother video
#             frame_interval = 1.0 / fps
#             frame_count = 0
            
#             try:
#                 while True:
#                     start = time.time()
                    
#                     # Capture high-quality screenshot
#                     png = await page.screenshot(type='png',timeout=60000)  # PNG is lossless, no quality param needed
#                     img = Image.open(io.BytesIO(png)).convert('RGB')
                    
#                     # Handle dimension changes
#                     w, h = img.size
#                     if (w, h) != (width, height):
#                         print(f" Dimension changed to {w}x{h}, recreating source...")
#                         # Would need to recreate video source here
#                         img = img.resize((width, height), Image.BILINEAR)
                    
#                     # Create VideoFrame and publish
#                     buf = img.tobytes()
#                     vf = rtc.VideoFrame(width, height, rtc.VideoBufferType.RGB24, buf)
#                     timestamp_us = int(time.time() * 1_000_000)
#                     video_src.capture_frame(vf, timestamp_us=timestamp_us)
                    
#                     frame_count += 1
#                     if frame_count % (fps * 5) == 0:
#                         print(f"📊 Published {frame_count} frames")
                    
#                     # Maintain frame rate
#                     elapsed = time.time() - start
#                     await asyncio.sleep(max(0, frame_interval - elapsed))
                    
#             except asyncio.CancelledError:
#                 print(" Stopping screen capture...")
#         # try:
#         #     asyncio.create_task(capture_and_publish())
#         # except Exception as e:
#         #     print(f"Error in screen capturing: {e}")
#         #     import traceback
#         #     traceback.print_exc()


        
#         # Start voice session and screen capture in parallel
#         print("🎙️ Starting voice assistant and screen capture...")
#         while True:
#             async with await runner.run() as session:
#                 print("🎙️ Voice assistant ready. Speak now...")
                
#                 with sd.RawInputStream(
#                     samplerate=SAMPLE_RATE,
#                     channels=CHANNEL,
#                     dtype="int16",
#                     blocksize=BLOCK,
#                     callback=mic_cb,
#                 ), sd.RawOutputStream(
#                     samplerate=SAMPLE_RATE,
#                     channels=CHANNEL,
#                     dtype="int16",
#                     blocksize=BLOCK,
#                     callback=spk_cb,
#                 ):
                    
#                     await asyncio.gather(
#                         send_mic_audio(session),
#                         receive_and_play(session),
#                         monitor_playback(),
#                         capture_and_publish()# Run screen capture in parallel
#                     )
    
#     except asyncio.CancelledError:
#         print("Screen share task cancelled...")
    
#     except Exception as e:
#         print(f"Error in publish_screen_sharess: {e}")
#         import traceback
#         traceback.print_exc()
#         raise
    
#     finally:
#         # Cleanup
#         print(" Cleaning up...")
        
#         if room_obj:
#             try:
#                 await room_obj.disconnect()
#             except Exception:
#                 pass
        
#         if browser:
#             try:
#                 await browser.close()
#             except Exception:
#                 pass
        
#         if playwright:
#             try:
#                 await playwright.stop()
#             except Exception:
#                 pass
        
#         print("Cleanup complete")

from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io, WorkerOptions
from livekit.plugins import openai, noise_cancellation
from config import LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
from openai.types import realtime
from livekit.plugins.openai.realtime import RealtimeModel
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")


server = AgentServer()

@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    
    model = RealtimeModel(
        voice="ash",
        modalities=["text", "audio"],
        input_audio_transcription=realtime.AudioTranscription(
            model="gpt-4o-transcribe"
        ),
        input_audio_noise_reduction="near_field",
        turn_detection=realtime.realtime_audio_input_turn_detection.SemanticVad(
            type="semantic_vad",
            create_response=True,
            eagerness="auto",
            interrupt_response=True,
        ),
    )
    
    session = AgentSession(llm=model)
    
    # Real-time transcript handlers
    @session.on("user_speech_committed")
    def on_user_speech(msg: agents.llm.ChatMessage):
        print(f"USER: {msg.content}")
        # logger.info(f"USER: {msg.content}")
    
    @session.on("agent_speech_committed") 
    def on_agent_speech(msg: agents.llm.ChatMessage):
        print(f"AGENT: {msg.content}")
        # logger.info(f"AGENT: {msg.content}")
    
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() 
                    if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP 
                    else noise_cancellation.BVC(),
            ),
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance. You should start by speaking in English."
    )


if __name__ == "__main__":
    agents.cli.run_app(
        WorkerOptions(
            entrypoint_fnc=my_agent,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET,
            ws_url=LIVEKIT_URL
        )
    )