"""
FlowSync AI - Autonomous Demo Video Generator (Browser-Compatible H.264 HD)
Generates an HTML5-compliant 1280x720 H.264 MP4 video demonstrating:
1. Multi-junction city simulation (J1, J2, J3, J4).
2. Dual-sensor detection: Acoustic siren sound frequency + YOLOv8 computer vision vehicle picture.
3. Signal preemption transition: Red light safely transitioning to Green light.
4. Inter-junction V2X communication: Junction 1 sending high-priority coordination packet to Junction 2.
5. Downstream green wave synchronization: Next junction clears corridor ahead of arrival.
"""

import math
import os
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def get_font(size: int, bold: bool = False):
    """Load a clean system font or fallback to PIL default."""
    candidates = [
        "C:\\Windows\\Fonts\\segoeui.ttf" if not bold else "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\arial.ttf" if not bold else "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\tahoma.ttf",
        "C:\\Windows\\Fonts\\consola.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_rounded_rect(draw, bbox, fill, outline=None, width=1, radius=8):
    """Draw a smooth rounded rectangle."""
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)

def generate_video(output_path: str, duration_sec: float = 18.0, fps: int = 24):
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    width, height = 1280, 720
    total_frames = int(duration_sec * fps)

    # Attempt browser-compatible H.264 encoding via imageio-ffmpeg
    use_imageio = False
    writer = None
    try:
        import imageio
        writer = imageio.get_writer(
            str(out_file),
            fps=fps,
            codec="libx264",
            pixelformat="yuv420p",
            quality=8,
            macro_block_size=None,
            ffmpeg_params=["-movflags", "faststart", "-preset", "fast"]
        )
        use_imageio = True
        print(f"Using imageio libx264 encoder for browser-compatible HTML5 video...")
    except Exception as e:
        print(f"imageio libx264 not available ({e}), falling back to cv2.VideoWriter...")
        import cv2
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(out_file), fourcc, fps, (width, height))

    # Fonts
    font_title = get_font(26, bold=True)
    font_section = get_font(18, bold=True)
    font_body = get_font(14, bold=False)
    font_bold = get_font(14, bold=True)
    font_mono = get_font(13, bold=False)
    font_mono_bold = get_font(13, bold=True)
    font_small = get_font(11, bold=False)

    # 4-Junction Network Coordinates
    j_nodes = {
        "J1": {"x": 190, "y": 200, "name": "J1: North Gate", "color": (124, 58, 237)},
        "J2": {"x": 490, "y": 200, "name": "J2: Market Road", "color": (2, 132, 199)},
        "J3": {"x": 190, "y": 480, "name": "J3: College Circle", "color": (5, 150, 105)},
        "J4": {"x": 490, "y": 480, "name": "J4: Hospital Road", "color": (234, 88, 12)},
    }

    print(f"Rendering {total_frames} frames ({duration_sec}s @ {fps}fps) to {out_file}...")

    for frame_idx in range(total_frames):
        t = frame_idx / fps

        # Canvas Setup
        img = Image.new("RGB", (width, height), (10, 14, 24))
        draw = ImageDraw.Draw(img)

        # Subtle dark tech grid lines
        for gx in range(0, width, 40):
            draw.line([(gx, 0), (gx, height)], fill=(17, 23, 38), width=1)
        for gy in range(0, height, 40):
            draw.line([(0, gy), (width, gy)], fill=(17, 23, 38), width=1)

        # ----------------- TOP HEADER BAR -----------------
        draw_rounded_rect(draw, (20, 15, width - 20, 68), fill=(16, 22, 38), outline=(42, 53, 76), radius=12)
        draw.text((36, 26), "🚦 FlowSync AI", font=font_title, fill=(240, 246, 252))
        draw.text((215, 33), "• Autonomous Urban Traffic Preemption & Multi-Junction DSRC Mesh", font=font_body, fill=(148, 163, 184))

        # Time code
        time_str = f"TIME: T+{t:04.1f}s | FPS: {fps}"
        draw.text((width - 240, 32), time_str, font=font_mono_bold, fill=(99, 102, 241))

        # Active Phase Pill
        if t < 3.5:
            phase_text = "STAGE 1: QUEUE CONGESTION (RED LIGHT)"
            pill_fill, pill_border, pill_color = (45, 20, 20), (239, 68, 68), (252, 165, 165)
        elif t < 7.5:
            phase_text = "STAGE 2: SOUND & PICTURE SENSOR DETECT"
            pill_fill, pill_border, pill_color = (48, 36, 12), (245, 158, 11), (253, 230, 138)
        elif t < 11.5:
            phase_text = "STAGE 3: RED ➔ GREEN SIGNAL PREEMPTION"
            pill_fill, pill_border, pill_color = (18, 48, 32), (16, 185, 129), (167, 243, 208)
        elif t < 15.0:
            phase_text = "STAGE 4: J1 ➔ J2 V2X INTER-COMMUNICATION"
            pill_fill, pill_border, pill_color = (36, 24, 60), (147, 51, 234), (221, 214, 254)
        else:
            phase_text = "STAGE 5: COORDINATED GREEN WAVE TRANSIT"
            pill_fill, pill_border, pill_color = (18, 42, 60), (6, 182, 212), (165, 243, 252)

        draw_rounded_rect(draw, (width - 620, 24, width - 260, 56), fill=pill_fill, outline=pill_border, radius=16)
        draw.text((width - 605, 32), phase_text, font=font_bold, fill=pill_color)

        # ----------------- LEFT PANEL: CITY ROAD NETWORK & SIMULATION -----------------
        draw_rounded_rect(draw, (20, 82, 670, 630), fill=(14, 19, 32), outline=(32, 44, 66), radius=14)
        draw.text((38, 96), "🏙️ City Road Network Topology & Micro-Simulation", font=font_section, fill=(241, 245, 249))
        draw.text((38, 122), "Coordinated Arterial Ring: J1 (North) ➔ J2 (Market) ➔ J4 (Hospital) ➔ J3 (College)", font=font_small, fill=(100, 116, 139))

        # Roads
        roads = [("J1", "J2"), ("J2", "J4"), ("J4", "J3"), ("J3", "J1")]
        for s_k, e_k in roads:
            p1 = j_nodes[s_k]
            p2 = j_nodes[e_k]
            # Road curb and asphalt
            draw.line([(p1["x"], p1["y"]), (p2["x"], p2["y"])], fill=(30, 41, 59), width=28)
            draw.line([(p1["x"], p1["y"]), (p2["x"], p2["y"])], fill=(15, 23, 42), width=20)
            # Dashed yellow lane divider
            dist = math.hypot(p2["x"] - p1["x"], p2["y"] - p1["y"])
            steps = int(dist // 22)
            for s in range(0, steps, 2):
                f1 = s / steps
                f2 = (s + 1) / steps
                xa = p1["x"] + (p2["x"] - p1["x"]) * f1
                ya = p1["y"] + (p2["y"] - p1["y"]) * f1
                xb = p1["x"] + (p2["x"] - p1["x"]) * f2
                yb = p1["y"] + (p2["y"] - p1["y"]) * f2
                draw.line([(xa, ya), (xb, yb)], fill=(203, 160, 40), width=2)

        # Inbound approach road to J1 (from West)
        draw.line([(40, 200), (190, 200)], fill=(30, 41, 59), width=28)
        draw.line([(40, 200), (190, 200)], fill=(15, 23, 42), width=20)

        # ----------------- VEHICLE DYNAMICS -----------------
        if t < 3.5:
            amb_x, amb_y = 90, 200
        elif t < 7.5:
            amb_x = 90 + (t - 3.5) * 8
            amb_y = 200
        elif t < 11.5:
            prog = (t - 7.5) / 4.0
            amb_x = 122 + prog * 130
            amb_y = 200
        elif t < 15.0:
            prog = (t - 11.5) / 3.5
            amb_x = 252 + prog * 238
            amb_y = 200
        else:
            prog = (t - 15.0) / 3.0
            amb_x = 490
            amb_y = 200 + prog * 160

        # Civilian queue cars
        if t < 9.5:
            draw_rounded_rect(draw, (138, 191, 163, 209), fill=(51, 65, 85), outline=(100, 116, 139), radius=4)
            draw_rounded_rect(draw, (168, 191, 188, 209), fill=(71, 85, 105), outline=(148, 163, 184), radius=4)
        else:
            car1_x = 168 + (t - 9.5) * 65
            draw_rounded_rect(draw, (car1_x, 191, car1_x + 22, 209), fill=(51, 65, 85), radius=4)

        # Emergency Vehicle (Ambulance with siren dome)
        siren_strobe = int(t * 8) % 2 == 0
        siren_clr = (239, 68, 68) if siren_strobe else (59, 130, 246)
        draw_rounded_rect(draw, (amb_x - 18, amb_y - 10, amb_x + 18, amb_y + 10), fill=(255, 255, 255), outline=(226, 232, 240), radius=5)
        # Red cross stripe
        draw.rectangle([(amb_x - 16, amb_y - 3), (amb_x + 16, amb_y + 3)], fill=(239, 68, 68))
        # Siren dome
        draw.ellipse([(amb_x - 4, amb_y - 9), (amb_x + 4, amb_y - 3)], fill=siren_clr)

        # Siren acoustic rings
        if 3.5 <= t <= 12.0:
            for ring_i in range(1, 3):
                wave_r = int(((t * 3.5 + ring_i * 0.3) % 1.0) * 48) + 12
                draw.ellipse([(amb_x - wave_r, amb_y - wave_r), (amb_x + wave_r, amb_y + wave_r)], outline=(245, 158, 11), width=2)
            draw.text((amb_x - 28, amb_y - 34), "🔊 96.4 dB SIREN", font=font_small, fill=(245, 158, 11))

        # ----------------- JUNCTION SIGNALS & NODES -----------------
        j1_sig = "RED" if t < 7.5 else ("YELLOW" if t < 8.5 else "GREEN")
        j2_sig = "RED" if t < 13.0 else ("YELLOW" if t < 14.2 else "GREEN")

        sig_states = {"J1": j1_sig, "J2": j2_sig, "J3": "RED", "J4": "GREEN" if t < 12.0 else "RED"}
        color_map = {"RED": (239, 68, 68), "YELLOW": (245, 158, 11), "GREEN": (16, 185, 129)}

        for j_key, j_data in j_nodes.items():
            jx, jy = j_data["x"], j_data["y"]
            sig = sig_states[j_key]
            sig_rgb = color_map[sig]

            # Aura bloom
            draw.ellipse([(jx - 26, jy - 26), (jx + 26, jy + 26)], outline=sig_rgb, width=1)
            draw.ellipse([(jx - 20, jy - 20), (jx + 20, jy + 20)], fill=(22, 30, 48), outline=sig_rgb, width=3)
            draw.ellipse([(jx - 9, jy - 9), (jx + 9, jy + 9)], fill=sig_rgb)

            # Node label
            draw.text((jx - 8, jy - 7), j_key, font=font_mono_bold, fill=(255, 255, 255))
            # Signal state tag
            draw_rounded_rect(draw, (jx - 46, jy + 25, jx + 46, jy + 44), fill=(15, 23, 42), outline=(51, 65, 85), radius=5)
            draw.text((jx - 38, jy + 28), f"{j_key} • {sig}", font=font_small, fill=sig_rgb)

        # ----------------- STAGE 4: WIRELESS V2X PACKET (J1 -> J2) -----------------
        if 11.5 <= t <= 15.5:
            p_prog = (t - 11.5) / 3.5
            px_val = 190 + p_prog * 300
            py_val = 170

            # Transmission beam
            draw.line([(190, 170), (490, 170)], fill=(124, 58, 237), width=2)
            # Pulse ring
            rad_pulse = int(((t * 4) % 1.0) * 18) + 6
            draw.ellipse([(px_val - rad_pulse, py_val - rad_pulse), (px_val + rad_pulse, py_val + rad_pulse)], outline=(192, 132, 252), width=2)

            # High-priority data packet badge
            draw_rounded_rect(draw, (px_val - 42, py_val - 15, px_val + 42, py_val + 15), fill=(88, 28, 135), outline=(216, 180, 254), radius=6)
            draw.text((px_val - 36, py_val - 8), "⚡ V2X MSG", font=font_bold, fill=(255, 255, 255))

            # Floating callout
            draw_rounded_rect(draw, (220, 110, 460, 155), fill=(24, 18, 44), outline=(147, 51, 234), radius=8)
            draw.text((230, 116), "📡 DSRC / C-V2X PACKET IN FLIGHT:", font=font_bold, fill=(216, 180, 254))
            draw.text((230, 134), f"ETA to J2: {max(0.1, 4.2 - (t - 11.5) * 1.2):.1f}s | Lock Green Corridor", font=font_mono, fill=(243, 232, 255))

        # ----------------- RIGHT PANEL TOP: DUAL-SENSOR DETECTION HUD -----------------
        draw_rounded_rect(draw, (690, 82, 1260, 380), fill=(14, 19, 32), outline=(32, 44, 66), radius=14)
        draw.text((708, 96), "🎯 Dual Edge Sensor Detection Pipeline", font=font_section, fill=(241, 245, 249))

        # SUB-PANEL A: AI CAMERA PICTURE SENSOR (YOLOv8)
        draw_rounded_rect(draw, (708, 126, 965, 365), fill=(18, 24, 40), outline=(51, 65, 85), radius=8)
        draw.text((720, 136), "📷 YOLOv8 Picture Camera (J1-Approach)", font=font_bold, fill=(56, 189, 248))

        # Camera viewport
        draw_rounded_rect(draw, (720, 160, 953, 310), fill=(10, 14, 23), outline=(71, 85, 105), radius=6)
        scan_line_y = 165 + int((t * 70) % 135)
        draw.line([(722, scan_line_y), (951, scan_line_y)], fill=(56, 189, 248), width=1)

        if t >= 2.5:
            bb_w = min(120, int(70 + (t - 2.5) * 10))
            bb_h = min(75, int(45 + (t - 2.5) * 6))
            bb_x = 836 - bb_w // 2
            bb_y = 235 - bb_h // 2
            cv_conf = min(99.4, 88.0 + (t - 2.5) * 2.5) if t < 8 else 99.4

            draw.rectangle([(bb_x, bb_y), (bb_x + bb_w, bb_y + bb_h)], outline=(16, 185, 129), width=2)
            draw.rectangle([(bb_x, bb_y - 18), (bb_x + 130, bb_y)], fill=(16, 185, 129))
            draw.text((bb_x + 4, bb_y - 15), f"AMBULANCE: {cv_conf:.1f}%", font=font_mono_bold, fill=(0, 0, 0))

            dist_m = max(2, int(45 - (t - 2.5) * 7))
            draw.text((725, 320), f"Track: #EM-01 | Dist: {dist_m}m | Speed: 52km/h", font=font_mono, fill=(16, 185, 129))
            draw.text((725, 342), "Status: 🟢 Confirmed Picture Target", font=font_small, fill=(203, 213, 225))
        else:
            draw.text((750, 228), "[SCANNING APPROACH]", font=font_mono, fill=(100, 116, 139))
            draw.text((725, 325), "Status: Standby / Passive Monitoring", font=font_small, fill=(148, 163, 184))

        # SUB-PANEL B: ACOUSTIC SIREN SENSOR (SOUND)
        draw_rounded_rect(draw, (985, 126, 1242, 365), fill=(18, 24, 40), outline=(51, 65, 85), radius=8)
        draw.text((997, 136), "🔊 Acoustic Siren Sensor (Array)", font=font_bold, fill=(245, 158, 11))

        # Oscilloscope Box
        draw_rounded_rect(draw, (997, 160, 1230, 260), fill=(10, 14, 23), outline=(71, 85, 105), radius=6)

        # Waveform points
        is_siren = t >= 3.0
        amp = 36 if is_siren else 7
        freq = 0.15 if is_siren else 0.05
        wave_clr = (245, 158, 11) if is_siren else (71, 85, 105)

        w_pts = []
        for xs in range(998, 1230, 3):
            y_v = 210 + math.sin((xs * freq) + (t * 18)) * amp
            if is_siren:
                y_v += math.cos((xs * 0.04) + (t * 6)) * 8
            w_pts.append((xs, int(y_v)))

        for i in range(len(w_pts) - 1):
            draw.line([w_pts[i], w_pts[i + 1]], fill=wave_clr, width=2)

        # Equalizer bars
        for b_i in range(12):
            bx = 1005 + b_i * 18
            bh = int(10 + math.sin(t * 12 + b_i) * 15 + 18) if is_siren else int(5 + (b_i % 3) * 4)
            draw.line([(bx, 255), (bx, 255 - bh)], fill=(245, 158, 11) if is_siren else (51, 65, 85), width=8)

        if is_siren:
            db_val = min(96.8, 78.0 + (t - 3.0) * 3.5) if t < 8 else 96.4
            draw.text((1000, 275), f"Decibels: {db_val:.1f} dB (Threshold: 85 dB)", font=font_mono, fill=(245, 158, 11))
            draw.text((1000, 298), "Frequency: 940 Hz – 1450 Hz (Wail)", font=font_mono, fill=(253, 230, 138))
            draw.text((1000, 320), "Acoustic Siren Match: 99.2% MATCH", font=font_bold, fill=(16, 185, 129))
            draw.text((1000, 342), "Status: 🚨 Dual Confirmation Verified", font=font_small, fill=(203, 213, 225))
        else:
            draw.text((1000, 275), "Decibels: 58.2 dB (Ambient Traffic)", font=font_mono, fill=(148, 163, 184))
            draw.text((1000, 298), "Frequency: Broadband Noise", font=font_mono, fill=(100, 116, 139))
            draw.text((1000, 320), "Acoustic Siren Match: 0.0%", font=font_bold, fill=(148, 163, 184))
            draw.text((1000, 342), "Status: Idle / Listening", font=font_small, fill=(100, 116, 139))

        # ----------------- RIGHT PANEL BOTTOM: ACTUATOR & TELEMETRY CONSOLE -----------------
        draw_rounded_rect(draw, (690, 395, 1260, 630), fill=(14, 19, 32), outline=(32, 44, 66), radius=14)
        draw.text((708, 410), "⚡ Actuator Relay & V2X Inter-Junction Packet Protocol", font=font_section, fill=(241, 245, 249))

        # 3-Light Housing (J1 Actuator)
        draw_rounded_rect(draw, (710, 440, 830, 615), fill=(18, 24, 40), outline=(51, 65, 85), radius=8)
        draw.text((722, 450), "J1 Actuator", font=font_bold, fill=(203, 213, 225))
        draw_rounded_rect(draw, (735, 475, 805, 595), fill=(10, 14, 23), outline=(71, 85, 105), radius=16)

        r_lit = j1_sig == "RED"
        y_lit = j1_sig == "YELLOW"
        g_lit = j1_sig == "GREEN"

        draw.ellipse([(750, 485), (790, 515)], fill=(239, 68, 68) if r_lit else (60, 20, 20), outline=(239, 68, 68) if r_lit else None, width=2)
        draw.ellipse([(750, 525), (790, 555)], fill=(245, 158, 11) if y_lit else (60, 45, 15), outline=(245, 158, 11) if y_lit else None, width=2)
        draw.ellipse([(750, 565), (790, 595)], fill=(16, 185, 129) if g_lit else (15, 50, 30), outline=(16, 185, 129) if g_lit else None, width=2)

        if r_lit:
            draw.ellipse([(745, 480), (795, 520)], outline=(239, 68, 68), width=1)
        if y_lit:
            draw.ellipse([(745, 520), (795, 560)], outline=(245, 158, 11), width=1)
        if g_lit:
            draw.ellipse([(745, 560), (795, 600)], outline=(16, 185, 129), width=1)

        # Terminal Console
        draw_rounded_rect(draw, (845, 440, 1245, 615), fill=(10, 14, 23), outline=(51, 65, 85), radius=8)
        draw.text((858, 450), "📟 Inter-Junction DSRC Telemetry Console (NTCIP 1202)", font=font_mono, fill=(56, 189, 248))
        draw.line([(855, 470), (1235, 470)], fill=(30, 41, 59), width=1)

        logs = []
        if t < 3.5:
            logs.append(("[00:01:02]", "[IDLE]", "J1 Cyclic Controller: Northbound queue accumulating (12 veh).", (148, 163, 184)))
            logs.append(("[00:01:03]", "[LOCK]", "J1 Signal State = RED. Opposing Phase = ACTIVE.", (239, 68, 68)))
            logs.append(("[00:01:04]", "[MESH]", "Mesh ping J1 <-> J2 latency: 1.8ms. Link healthy.", (56, 189, 248)))
        elif t < 7.5:
            logs.append(("[00:01:05]", "[SENSOR-SOUND]", "Mic array triggered: 96.4 dB @ 1.2 kHz siren signature.", (245, 158, 11)))
            logs.append(("[00:01:06]", "[SENSOR-PICT] ", "YOLOv8 vision verified approaching AMBULANCE #EM-01.", (16, 185, 129)))
            logs.append(("[00:01:07]", "[PREEMPT-REQ] ", "Dual-sensor consensus achieved! Initiating emergency clear.", (216, 180, 254)))
        elif t < 11.5:
            logs.append(("[00:01:08]", "[ACTUATOR]    ", "Executing clearance safety interval (Yellow 1.5s).", (245, 158, 11)))
            logs.append(("[00:01:09]", "[SIGNAL-GREEN]", "J1 SNAPPED TO GREEN. Approach corridor preempted.", (16, 185, 129)))
            logs.append(("[00:01:10]", "[DISPATCH]    ", "Ambulance traversing J1. Broadcasting to downstream node...", (56, 189, 248)))
        elif t < 15.0:
            logs.append(("[00:01:11]", "[V2X-TX: J1]  ", "BROADCAST -> MSG_ID#8834 TARGET: J2 (Market Road).", (192, 132, 252)))
            logs.append(("[00:01:12]", "[PAYLOAD]     ", "{ 'preempt': True, 'eta_sec': 4.2, 'lane': 'NORTH_EAST' }", (243, 232, 255)))
            logs.append(("[00:01:13]", "[V2X-RX: J2]  ", "J2 ACKNOWLEDGED. Opposing phase yellow clearance initiated.", (16, 185, 129)))
        else:
            logs.append(("[00:01:14]", "[GREEN-WAVE]  ", "J2 SYNCHRONIZED GREEN. Zero stop corridor established.", (16, 185, 129)))
            logs.append(("[00:01:15]", "[TELEMETRY]   ", "Transit delay reduction: 84.2%. Spillback risk: ZERO.", (56, 189, 248)))
            logs.append(("[00:01:16]", "[SUCCESS]     ", "Emergency corridor cleared smoothly across multi-junction grid.", (240, 246, 252)))

        for l_i, (ts, tag, text, clr) in enumerate(logs):
            ly = 482 + l_i * 24
            draw.text((858, ly), ts, font=font_mono, fill=(100, 116, 139))
            draw.text((930, ly), tag, font=font_mono_bold, fill=clr)
            draw.text((1035, ly), text[:38], font=font_mono, fill=(226, 232, 240))

        # ----------------- BOTTOM NARRATION CAPTION -----------------
        draw_rounded_rect(draw, (20, 642, width - 20, 706), fill=(18, 25, 42), outline=(56, 189, 248), radius=10)

        if t < 3.5:
            b_title = "🚦 SCENE 1: CONGESTION AT RED SIGNAL"
            b_desc = "Junction 1 holds traffic at RED. Queue builds up with high wait times under standard fixed cyclic timings."
        elif t < 7.5:
            b_title = "🔊📷 SCENE 2: DUAL SENSOR DETECTION (SOUND & PICTURE)"
            b_desc = "Acoustic sensor identifies emergency siren decibels while YOLOv8 camera detects vehicle picture & class. Consensus is confirmed."
        elif t < 11.5:
            b_title = "🟢 SCENE 3: RED TURNS TO GREEN LIGHT (DYNAMIC PREEMPTION)"
            b_desc = "The controller safely clears conflicting approaches and turns the RED light into GREEN, allowing priority vehicle to pass instantly."
        elif t < 15.0:
            b_title = "📡 SCENE 4: INTER-JUNCTION COMMUNICATION (J1 ➔ J2)"
            b_desc = "Junction 1 sends a high-priority DSRC / C-V2X message packet to Junction 2 ahead of time with vehicle ETA and clearance request."
        else:
            b_title = "⚡ SCENE 5: NEXT JUNCTION COORDINATES GREEN WAVE"
            b_desc = "Junction 2 receives the message, clears cross-traffic, and turns GREEN before arrival. Continuous multi-junction green wave accomplished!"

        draw.text((36, 652), b_title, font=font_bold, fill=(56, 189, 248))
        draw.text((36, 676), b_desc, font=font_body, fill=(241, 245, 249))

        # Write frame
        np_frame = np.array(img)
        if use_imageio:
            writer.append_data(np_frame)
        else:
            import cv2
            writer.write(cv2.cvtColor(np_frame, cv2.COLOR_RGB2BGR))

        if frame_idx % (fps * 3) == 0:
            print(f"  > Rendered frame {frame_idx}/{total_frames} ({t:.1f}s)...")

    if use_imageio:
        writer.close()
    else:
        writer.release()

    print(f"Video generation complete! File saved to {out_file} (Size: {os.path.getsize(out_file)} bytes)")

if __name__ == "__main__":
    out_p = Path(__file__).parent / "assets" / "flowsync_simulation_demo.mp4"
    generate_video(str(out_p), duration_sec=18.0, fps=24)
