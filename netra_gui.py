"""Interactive 3D-style NETRA wearable sensor monitor."""

from __future__ import annotations

import argparse
import csv
import math
import queue
import threading
import time
import tkinter as tk
from collections import deque
from dataclasses import dataclass

import serial


@dataclass
class Sample:
    distance: float
    ax: float
    ay: float
    az: float
    gx: float
    gy: float
    gz: float
    temperature: float
    status: str
    received_at: float

    @property
    def motion(self) -> float:
        return math.sqrt(self.gx * self.gx + self.gy * self.gy + self.gz * self.gz)


def number(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return math.nan


class SerialReader(threading.Thread):
    """Reconnectable reader that does not force the ESP32-C6 into download mode."""

    def __init__(self, port: str, baud: int, messages: queue.Queue):
        super().__init__(daemon=True)
        self.port = port
        self.baud = baud
        self.messages = messages
        self.stop_event = threading.Event()
        self.reset_event = threading.Event()

    def request_reset(self) -> None:
        self.reset_event.set()

    def stop(self) -> None:
        self.stop_event.set()

    def run(self) -> None:
        while not self.stop_event.is_set():
            try:
                connection = serial.Serial()
                connection.port = self.port
                connection.baudrate = self.baud
                connection.timeout = 0.25
                # Released states: GPIO0 high and EN high. PySerial defaults to
                # asserted control lines, which can leave an ESP32-C6 in ROM.
                connection.dtr = False
                connection.rts = False
                connection.open()
                self.messages.put(("connection", f"LIVE / {self.port} / {self.baud} baud"))
                with connection:
                    while not self.stop_event.is_set():
                        if self.reset_event.is_set():
                            self.reset_event.clear()
                            connection.dtr = False
                            connection.rts = True
                            time.sleep(0.10)
                            connection.rts = False
                            self.messages.put(("connection", "C6 reset requested - waiting for sketch"))
                        raw = connection.readline().decode("utf-8", errors="replace").strip()
                        if not raw:
                            continue
                        if "waiting for download" in raw.lower():
                            self.messages.put(("bootloader", "C6 IS IN ROM DOWNLOAD MODE - CLICK RESET C6"))
                            continue
                        if raw.startswith("ESP-ROM:"):
                            self.messages.put(("connection", "C6 rebooting - waiting for NETRA sketch"))
                            continue
                        fields = next(csv.reader([raw]))
                        if len(fields) != 10 or fields[0] == "distance_cm":
                            continue
                        self.messages.put(("sample", Sample(
                            number(fields[0]), number(fields[2]), number(fields[3]),
                            number(fields[4]), number(fields[5]), number(fields[6]),
                            number(fields[7]), number(fields[8]), fields[9], time.monotonic()
                        )))
            except (serial.SerialException, OSError) as exc:
                self.messages.put(("connection", f"WAITING FOR {self.port} / {exc}"))
                self.stop_event.wait(1.5)


class NetraApp:
    BG = "#050b14"
    PANEL = "#0a1726"
    PANEL_2 = "#0e2033"
    GRID = "#15334a"
    TEXT = "#edf8ff"
    MUTED = "#7392aa"
    CYAN = "#35d9ff"
    GREEN = "#45e69f"
    AMBER = "#ffc15b"
    RED = "#ff607b"
    AXIS = {"x": "#ff657e", "y": "#52e7a6", "z": "#55a7ff"}
    PRESENCE_LIMIT_CM = 250.0

    def __init__(self, root: tk.Tk, port: str, baud: int):
        self.root = root
        root.title("NETRA 3D | Wearable Spatial Intelligence")
        root.geometry("1440x860")
        root.minsize(1120, 700)
        root.configure(bg=self.BG)
        self.messages: queue.Queue = queue.Queue()
        self.reader = SerialReader(port, baud, self.messages)
        self.reader.start()
        self.sample: Sample | None = None
        self.display_sample: Sample | None = None
        self.connection_text = f"OPENING {port}"
        self.demo = False
        self.environment_mode = "FIELD"
        self.phase = 0.0
        self.frame_count = 0
        self.started_at = time.monotonic()
        self.yaw = 26.0
        self.pitch = 10.0
        self.zoom = 1.0
        self.drag_origin: tuple[int, int, float, float] | None = None
        self.histories = {name: deque([0.0] * 100, maxlen=100)
                          for name in ("ax", "ay", "az", "gx", "gy", "gz")}
        self.sample_times: deque[float] = deque(maxlen=40)
        self.last_history_sample = 0.0
        self._build()
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.tick()

    def _label(self, parent, text, size=10, color=None, weight="normal", **pack):
        label = tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color or self.TEXT,
                         font=("Segoe UI" if weight == "normal" else "Segoe UI Semibold", size))
        if pack:
            label.pack(**pack)
        return label

    def _button(self, parent, text, command, accent=False):
        return tk.Button(parent, text=text, command=command, bg=self.CYAN if accent else self.PANEL_2,
                         fg=self.BG if accent else self.TEXT, activebackground=self.GREEN,
                         activeforeground=self.BG, relief="flat", bd=0, padx=14, pady=7,
                         cursor="hand2", font=("Segoe UI Semibold", 9))

    def _build(self) -> None:
        header = tk.Frame(self.root, bg=self.BG)
        header.pack(fill="x", padx=24, pady=(16, 10))
        self._label(header, "NETRA", 25, self.CYAN, "bold", side="left")
        self._label(header, "  WEARABLE SPATIAL INTELLIGENCE / 3D DIGITAL TWIN",
                    10, self.MUTED).pack(side="left", pady=(9, 0))
        self.status_dot = self._label(header, "●", 17, self.AMBER)
        self.status_dot.pack(side="right")
        self.connection = self._label(header, self.connection_text, 9, self.MUTED)
        self.connection.pack(side="right", padx=8)

        toolbar = tk.Frame(self.root, bg=self.BG)
        toolbar.pack(fill="x", padx=24, pady=(0, 10))
        self.demo_button = self._button(toolbar, "DEMO: OFF", self.toggle_demo)
        self.demo_button.pack(side="left", padx=(0, 7))
        self._button(toolbar, "RESET C6", self.reader.request_reset).pack(side="left", padx=(0, 7))
        self._button(toolbar, "RESET VIEW", self.reset_view).pack(side="left", padx=(0, 7))
        self.environment_button = self._button(toolbar, "WORLD: FIELD", self.toggle_environment)
        self.environment_button.pack(side="left")
        self._label(toolbar, "Drag to orbit  •  Wheel to zoom  •  IMU drives posture  •  Ultrasonic maps clearance",
                    9, self.MUTED).pack(side="right")

        body = tk.Frame(self.root, bg=self.BG)
        body.pack(fill="both", expand=True, padx=24, pady=(0, 22))
        left = tk.Frame(body, bg=self.PANEL)
        left.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(left, bg=self.PANEL, highlightthickness=0, cursor="fleur")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self.begin_orbit)
        self.canvas.bind("<B1-Motion>", self.orbit)
        self.canvas.bind("<MouseWheel>", self.wheel)

        side = tk.Frame(body, bg=self.BG, width=365)
        side.pack(side="right", fill="y", padx=(14, 0))
        side.pack_propagate(False)

        status = tk.Frame(side, bg=self.PANEL_2, padx=15, pady=12)
        status.pack(fill="x", pady=(0, 10))
        self._label(status, "OBSTACLE DETECTION", 9, self.MUTED, "bold", anchor="w")
        self.presence_label = self._label(status, "SCANNING PATH", 18, self.AMBER, "bold", anchor="w")
        row = tk.Frame(status, bg=self.PANEL_2)
        row.pack(fill="x", pady=(5, 0))
        self.distance_label = self._label(row, "RANGE -- cm", 10, self.TEXT)
        self.distance_label.pack(side="left")
        self.motion_label = self._label(row, "MOTION -- dps", 10, self.TEXT)
        self.motion_label.pack(side="right")

        self.imu_labels: dict[str, tk.Label] = {}
        self.accel_graph = self._imu_card(side, "ACCELEROMETER", "g", ("ax", "ay", "az"))
        self.gyro_graph = self._imu_card(side, "GYROSCOPE", "°/s", ("gx", "gy", "gz"))

        orientation = tk.Frame(side, bg=self.PANEL_2, padx=15, pady=10)
        orientation.pack(fill="x", pady=(0, 10))
        self._label(orientation, "WEARABLE ORIENTATION", 9, self.MUTED, "bold", anchor="w")
        line = tk.Frame(orientation, bg=self.PANEL_2)
        line.pack(fill="x", pady=(5, 0))
        self.tilt_label = self._label(line, "TILT --°", 12, self.TEXT, "bold")
        self.tilt_label.pack(side="left")
        self.temp_label = self._label(line, "TEMP --°C", 12, self.TEXT, "bold")
        self.temp_label.pack(side="right")
        self.health_label = self._label(orientation, "SENSOR STREAM WAITING", 9, self.AMBER)
        self.health_label.pack(anchor="w", pady=(7, 0))

        analytics = tk.Frame(side, bg=self.PANEL_2, padx=15, pady=10)
        analytics.pack(fill="x")
        self._label(analytics, "SPATIAL ANALYTICS", 9, self.MUTED, "bold", anchor="w")
        metrics = tk.Frame(analytics, bg=self.PANEL_2)
        metrics.pack(fill="x", pady=(7, 0))
        left_metrics = tk.Frame(metrics, bg=self.PANEL_2)
        left_metrics.pack(side="left", fill="x", expand=True)
        right_metrics = tk.Frame(metrics, bg=self.PANEL_2)
        right_metrics.pack(side="right", fill="x", expand=True)
        self.posture_label = self._label(left_metrics, "POSTURE --", 10, self.TEXT, "bold")
        self.posture_label.pack(anchor="w")
        self.gravity_label = self._label(left_metrics, "LOAD -- g", 9, self.MUTED)
        self.gravity_label.pack(anchor="w", pady=(3, 0))
        self.clearance_label = self._label(right_metrics, "CLEARANCE --", 10, self.TEXT, "bold")
        self.clearance_label.pack(anchor="e")
        self.stream_label = self._label(right_metrics, "STREAM -- Hz", 9, self.MUTED)
        self.stream_label.pack(anchor="e", pady=(3, 0))

    def _imu_card(self, parent, title: str, unit: str, axes: tuple[str, str, str]) -> tk.Canvas:
        card = tk.Frame(parent, bg=self.PANEL_2, padx=15, pady=10)
        card.pack(fill="x", pady=(0, 10))
        head = tk.Frame(card, bg=self.PANEL_2)
        head.pack(fill="x")
        self._label(head, title, 9, self.MUTED, "bold").pack(side="left")
        self._label(head, unit, 8, self.MUTED).pack(side="right")
        values = tk.Frame(card, bg=self.PANEL_2)
        values.pack(fill="x", pady=(4, 2))
        for axis in axes:
            cell = tk.Frame(values, bg=self.PANEL_2)
            cell.pack(side="left", fill="x", expand=True)
            self._label(cell, axis[-1].upper(), 8, self.AXIS[axis[-1]], "bold").pack(anchor="w")
            label = self._label(cell, "--", 13, self.TEXT, "bold")
            label.pack(anchor="w")
            self.imu_labels[axis] = label
        graph = tk.Canvas(card, height=62, bg="#07121f", highlightthickness=0)
        graph.pack(fill="x", pady=(5, 0))
        graph.axes = axes  # type: ignore[attr-defined]
        return graph

    def obstacle_detected(self, sample: Sample | None) -> bool:
        return bool(sample and "RANGE_OK" in sample.status and not math.isnan(sample.distance)
                    and 2.0 <= sample.distance <= self.PRESENCE_LIMIT_CM)

    def toggle_demo(self) -> None:
        self.demo = not self.demo
        self.demo_button.configure(text=f"DEMO: {'ON' if self.demo else 'OFF'}",
                                   bg=self.GREEN if self.demo else self.PANEL_2,
                                   fg=self.BG if self.demo else self.TEXT)

    def toggle_environment(self) -> None:
        self.environment_mode = "LAB" if self.environment_mode == "FIELD" else "FIELD"
        self.environment_button.configure(text=f"WORLD: {self.environment_mode}")

    def reset_view(self) -> None:
        self.yaw, self.pitch, self.zoom = 26.0, 10.0, 1.0

    def begin_orbit(self, event) -> None:
        self.drag_origin = (event.x, event.y, self.yaw, self.pitch)

    def orbit(self, event) -> None:
        if self.drag_origin:
            x, y, yaw, pitch = self.drag_origin
            self.yaw = yaw + (event.x - x) * 0.35
            self.pitch = max(-20.0, min(35.0, pitch - (event.y - y) * 0.25))

    def wheel(self, event) -> None:
        self.zoom = max(0.62, min(1.65, self.zoom * (1.08 if event.delta > 0 else 0.92)))

    def demo_sample(self) -> Sample:
        t = time.monotonic()
        cycle = math.sin(t * 2.2)
        return Sample(115 + 24 * math.sin(t * 0.65),
                      0.16 * cycle, 0.08 * math.sin(t * 1.1), 0.98 + 0.07 * abs(cycle),
                      14 * math.cos(t * 2.2), 38 * cycle, 8 * math.sin(t * 0.9),
                      29.4 + 0.3 * math.sin(t * 0.2), "RANGE_OK|IMU_OK", time.monotonic())

    def project(self, point, width, height):
        x, y, z = point
        ya, pa = math.radians(self.yaw), math.radians(self.pitch)
        rx = x * math.cos(ya) + z * math.sin(ya)
        rz = -x * math.sin(ya) + z * math.cos(ya)
        ry = y * math.cos(pa) - rz * math.sin(pa)
        depth = y * math.sin(pa) + rz * math.cos(pa)
        scale = min(width / 8.0, height / 5.5) * self.zoom
        perspective = 1.0 / max(0.60, 1.0 + depth * 0.055)
        return width * 0.50 + rx * scale * perspective, height * 0.82 - ry * scale * perspective, depth

    def line3d(self, a, b, view_width, view_height, **style):
        pa = self.project(a, view_width, view_height)
        pb = self.project(b, view_width, view_height)
        self.canvas.create_line(pa[0], pa[1], pb[0], pb[1], **style)
        return pa, pb

    def polygon3d(self, points, width, height, **style):
        projected = [self.project(point, width, height) for point in points]
        return self.canvas.create_polygon(*[(p[0], p[1]) for p in projected], **style)

    @staticmethod
    def orientation(sample: Sample) -> tuple[float, float]:
        roll = math.degrees(math.atan2(sample.ay, sample.az))
        pitch = math.degrees(math.atan2(-sample.ax, math.sqrt(sample.ay ** 2 + sample.az ** 2)))
        return roll, pitch

    def draw_atmosphere(self, width: int, height: int) -> None:
        bands = ("#071523", "#091a2a", "#0a1d2d", "#0b2030", "#0c2333", "#0d2636")
        horizon = int(height * .58)
        for i, color in enumerate(bands):
            y0 = i * horizon / len(bands)
            y1 = (i + 1) * horizon / len(bands) + 1
            self.canvas.create_rectangle(0, y0, width, y1, fill=color, outline=color)
        self.canvas.create_rectangle(0, horizon, width, height, fill=self.PANEL, outline=self.PANEL)
        # A sparse star/particle field gives the digital world depth without visual noise.
        for i in range(28):
            x = (i * 173 + 41) % max(width, 1)
            y = (i * 67 + 23) % max(horizon, 1)
            radius = 1 if i % 4 else 2
            self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius,
                                    fill="#1b4b64", outline="")

    def draw_environment(self, width: int, height: int) -> None:
        if self.environment_mode == "LAB":
            # Instrumented motion-capture bay: rear wall, side frames and scan gates.
            self.polygon3d([(-4, 0, -4), (4, 0, -4), (4, 3, -4), (-4, 3, -4)],
                           width, height, fill="#0b1b29", outline="#24445a")
            for x in (-3.6, 3.6):
                for z in (-3.5, -1.5, .5, 2.5):
                    self.line3d((x, 0, z), (x, 2.6, z), width, height,
                                fill="#24465d", width=3)
                    self.line3d((x, 2.6, z), (-x, 2.6, z), width, height,
                                fill="#17364c", width=2)
            for y in (.6, 1.2, 1.8, 2.4):
                self.line3d((-4, y, -4), (4, y, -4), width, height,
                            fill="#112f43", width=1)
            self.canvas.create_text(width * .5, height * .16, text="NETRA MOTION CAPTURE BAY  /  ZONE 04",
                                    fill="#2f647e", font=("Consolas", 10))
        else:
            # Outdoor navigation lane with posts, rails and distant skyline blocks.
            self.polygon3d([(-1.15, .002, 4), (1.15, .002, 4), (1.15, .002, -4), (-1.15, .002, -4)],
                           width, height, fill="#0c1e28", outline="#1e4556")
            for z in (-3.6, -2.4, -1.2, 0, 1.2, 2.4, 3.6):
                for x in (-2.15, 2.15):
                    self.line3d((x, 0, z), (x, 1.15, z), width, height,
                                fill="#2a5364", width=4)
                    top = self.project((x, 1.18, z), width, height)
                    self.canvas.create_oval(top[0]-4, top[1]-4, top[0]+4, top[1]+4,
                                            fill=self.CYAN, outline="#b6f5ff")
            for x in (-2.15, 2.15):
                self.line3d((x, .62, -4), (x, .62, 4), width, height,
                            fill="#1a4051", width=2)
            for x, z, h in ((-3.3, -3.7, 1.5), (-2.7, -3.85, 2.2),
                            (2.7, -3.8, 1.8), (3.35, -3.65, 2.5)):
                self.polygon3d([(x-.35, 0, z), (x+.35, 0, z), (x+.35, h, z), (x-.35, h, z)],
                               width, height, fill="#102536", outline="#24506a")

    def draw_world_axes(self, width: int, height: int) -> None:
        origin = (width - 86, height - 70)
        self.canvas.create_text(origin[0], origin[1] + 42, text="WORLD FRAME",
                                fill=self.MUTED, font=("Segoe UI Semibold", 8))
        vectors = (("X", 34, 8, self.AXIS["x"]), ("Y", 0, -35, self.AXIS["y"]),
                   ("Z", -25, 18, self.AXIS["z"]))
        for label, dx, dy, color in vectors:
            self.canvas.create_line(origin[0], origin[1], origin[0]+dx, origin[1]+dy,
                                    fill=color, width=2, arrow=tk.LAST)
            self.canvas.create_text(origin[0]+dx*1.18, origin[1]+dy*1.18,
                                    text=label, fill=color, font=("Segoe UI Semibold", 8))

    def draw_minimap(self, width: int, sample: Sample | None, obstacle: bool) -> None:
        x0, y0, size = width - 188, 22, 160
        self.canvas.create_rectangle(x0, y0, x0+size, y0+126,
                                     fill="#07131f", outline="#21445b", width=1)
        self.canvas.create_text(x0+10, y0+9, anchor="nw", text="TOP-DOWN SENSOR MAP",
                                fill=self.MUTED, font=("Segoe UI Semibold", 8))
        cx, cy = x0 + size/2, y0 + 104
        for radius in (18, 36, 54):
            self.canvas.create_arc(cx-radius, cy-radius, cx+radius, cy+radius,
                                   start=35, extent=110, style="arc", outline="#17364b")
        self.canvas.create_polygon(cx, cy-7, cx-6, cy+7, cx+6, cy+7,
                                   fill=self.GREEN, outline="#c8fff0")
        self.canvas.create_line(cx, cy-8, cx, y0+36, fill="#236077", dash=(4, 4))
        if obstacle and sample:
            ratio = min(1.0, sample.distance / self.PRESENCE_LIMIT_CM)
            oy = cy - 18 - ratio * 51
            danger = sample.distance < 60
            color = self.RED if danger else self.AMBER
            self.canvas.create_rectangle(cx-10, oy-5, cx+10, oy+5, fill=color, outline="")
            self.canvas.create_text(cx+15, oy, anchor="w", text=f"{sample.distance:.0f} cm",
                                    fill=color, font=("Consolas", 8))

    def draw_grid(self, width, height) -> None:
        for n in range(-5, 6):
            color = self.GRID if n else "#24506b"
            self.line3d((n, 0, -5), (n, 0, 5), width, height, fill=color, width=1)
            self.line3d((-5, 0, n), (5, 0, n), width, height, fill=color, width=1)
        # Spatial range rings around the wearable/person.
        for radius in (0.75, 1.5, 2.25):
            points = []
            for i in range(41):
                a = i * math.tau / 40
                p = self.project((radius * math.cos(a), 0.006, radius * math.sin(a)), width, height)
                points.extend((p[0], p[1]))
            self.canvas.create_line(*points, fill="#123148", width=1)

    def draw_sensor_field(self, width, height, sample: Sample | None, obstacle: bool) -> None:
        # The ultrasonic module is part of the wearable node. It scans the path
        # ahead; it never controls whether the wearer/avatar is displayed.
        origin = (0.20, 0.56, -0.02)
        distance_world = min(3.3, max(0.48, sample.distance / 75.0)) if obstacle and sample else 3.3
        target = (0.10, 0.42, -distance_world)
        po = self.project(origin, width, height)
        pt = self.project(target, width, height)
        danger = bool(obstacle and sample and sample.distance < 60)
        color = self.RED if danger else (self.AMBER if obstacle else self.GREEN)
        # Layered beam edges make the ultrasonic field readable as a volume.
        for spread, beam_color in ((.18, "#17445a"), (.42, "#1d536a"), (.68, "#236077")):
            left = self.project((target[0]-spread, 0.12, target[2]), width, height)
            right = self.project((target[0]+spread, 0.12, target[2]), width, height)
            self.canvas.create_line(po[0], po[1], left[0], left[1], fill=beam_color, width=1)
            self.canvas.create_line(po[0], po[1], right[0], right[1], fill=beam_color, width=1)
        self.canvas.create_line(po[0], po[1], pt[0], pt[1], fill=color, width=2, dash=(6, 5))
        for offset in (-0.42, 0.42):
            edge = self.project((target[0] + offset, 0.18, target[2]), width, height)
            self.canvas.create_line(po[0], po[1], edge[0], edge[1], fill="#236077", width=1)
        self.canvas.create_text(po[0]-10, po[1]-12, text="HC-SR04", anchor="se", fill=self.CYAN,
                                font=("Segoe UI Semibold", 9), justify="right")

        if obstacle and sample:
            # A projected cuboid makes the detected object part of the same 3D
            # ecosystem and moves it spatially as measured range changes.
            x, z = target[0], target[2]
            corners = {
                "fl": (x-.38, 0, z+.25), "fr": (x+.38, 0, z+.25),
                "bl": (x-.38, 0, z-.25), "br": (x+.38, 0, z-.25),
                "ftl": (x-.38, .82, z+.25), "ftr": (x+.38, .82, z+.25),
                "btl": (x-.38, .82, z-.25), "btr": (x+.38, .82, z-.25),
            }
            front = [self.project(corners[n], width, height) for n in ("fl", "fr", "ftr", "ftl")]
            self.canvas.create_polygon(*[(p[0], p[1]) for p in front], fill="#3a1924" if danger else "#392f1b",
                                       outline=color, width=2)
            for a, b in (("fl","bl"),("fr","br"),("ftl","btl"),("ftr","btr"),
                         ("bl","br"),("bl","btl"),("br","btr"),("btl","btr")):
                self.line3d(corners[a], corners[b], width, height, fill=color, width=2)
            top = self.project((x, .92, z), width, height)
            warning = "DANGER" if danger else "OBSTACLE"
            self.canvas.create_text(top[0], top[1], text=f"{warning}\n{sample.distance:.1f} cm",
                                    fill=color, font=("Segoe UI Semibold", 10), justify="center")
        else:
            self.canvas.create_text(pt[0], pt[1], text="PATH CLEAR / SCANNING",
                                    fill=self.GREEN, font=("Segoe UI Semibold", 9))

    def draw_person(self, width, height, sample: Sample) -> None:
        movement = min(sample.motion / 120.0, 1.0)
        roll, pitch = self.orientation(sample)
        torso_x = max(-.22, min(.22, roll / 120.0))
        torso_z = max(-.20, min(.20, pitch / 120.0))
        self.phase += 0.035 + movement * 0.09
        swing = math.sin(self.phase) * 0.28 * movement
        lift = abs(math.sin(self.phase)) * 0.13 * movement
        joints = {
            "pelvis": (0, 1.02, 0), "chest": (torso_x, 1.54, torso_z),
            "neck": (torso_x*1.2, 1.72, torso_z*1.2),
            "head": (torso_x*1.35, 1.94, torso_z*1.35),
            "ls": (-.30+torso_x, 1.57, torso_z), "rs": (.30+torso_x, 1.57, torso_z),
            "le": (-.45+torso_x, 1.27, .04+swing*.2+torso_z),
            "re": (.45+torso_x, 1.27, -.04-swing*.2+torso_z),
            "lh": (-.36, .99, .08+swing*.3), "rh": (.36, .99, -.08-swing*.3),
            "lhip": (-.15, 1.01, 0), "rhip": (.15, 1.01, 0),
            "lknee": (-.17-swing, .53+lift, .05+swing*.35),
            "rknee": (.17+swing, .53+lift, -.05-swing*.35),
            "lankle": (-.18+swing*.45, .06+lift*.15, -.03-swing*.2),
            "rankle": (.18-swing*.45, .06+lift*.15, .03+swing*.2),
        }
        bones = [("pelvis","chest"),("chest","neck"),("ls","rs"),("ls","le"),("le","lh"),
                 ("rs","re"),("re","rh"),("lhip","rhip"),("lhip","lknee"),("lknee","lankle"),
                 ("rhip","rknee"),("rknee","rankle")]
        # Shadow gives the avatar a grounded 3D volume.
        shadow = [self.project((.58*math.cos(i*math.tau/30), .01, .32*math.sin(i*math.tau/30)), width, height)
                  for i in range(31)]
        self.canvas.create_polygon(*[(p[0], p[1]) for p in shadow], fill="#06101a", outline="#15344b")
        for a, b in bones:
            self.line3d(joints[a], joints[b], width, height, fill="#d9edfa", width=12,
                        capstyle=tk.ROUND)
            self.line3d(joints[a], joints[b], width, height, fill="#5f8299", width=3,
                        capstyle=tk.ROUND)
        head = self.project(joints["head"], width, height)
        radius = 27 * self.zoom
        self.canvas.create_oval(head[0]-radius, head[1]-radius, head[0]+radius, head[1]+radius,
                                fill="#16344b", outline=self.TEXT, width=3)
        # Sensor-equipped right knee: pad, straps, pulse and local IMU axes.
        knee = self.project(joints["rknee"], width, height)
        pulse = 5 + movement * (8 + 5 * math.sin(self.phase * 3))
        self.canvas.create_oval(knee[0]-25-pulse, knee[1]-25-pulse, knee[0]+25+pulse, knee[1]+25+pulse,
                                outline=self.GREEN, width=2)
        self.canvas.create_oval(knee[0]-24, knee[1]-29, knee[0]+24, knee[1]+29,
                                fill="#16dca0", outline="#d8fff3", width=3)
        self.canvas.create_line(knee[0]-38, knee[1]-15, knee[0]+38, knee[1]-15, fill="#1f806e", width=4)
        self.canvas.create_line(knee[0]-38, knee[1]+15, knee[0]+38, knee[1]+15, fill="#1f806e", width=4)
        self.canvas.create_text(knee[0], knee[1], text="IMU", fill=self.BG,
                                font=("Segoe UI Black", 9))
        for axis, delta in (("x", (36, 0)), ("y", (0, -36)), ("z", (25, 22))):
            self.canvas.create_line(knee[0], knee[1], knee[0]+delta[0], knee[1]+delta[1],
                                    fill=self.AXIS[axis], width=2, arrow=tk.LAST)
            self.canvas.create_text(knee[0]+delta[0]*1.12, knee[1]+delta[1]*1.12,
                                    text=axis.upper(), fill=self.AXIS[axis], font=("Segoe UI Semibold", 8))
        self.canvas.create_text(knee[0]+48, knee[1]-44, anchor="sw", text="NETRA KNEE NODE",
                                fill=self.GREEN, font=("Segoe UI Semibold", 10))
        self.canvas.create_text(knee[0]+48, knee[1]-29, anchor="sw",
                                text=f"ROLL {roll:+.1f}°  PITCH {pitch:+.1f}°",
                                fill=self.MUTED, font=("Consolas", 8))

    def draw_scene(self, sample: Sample | None) -> None:
        c = self.canvas
        c.delete("all")
        width, height = max(c.winfo_width(), 700), max(c.winfo_height(), 560)
        avatar_sample = sample or Sample(math.nan, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0,
                                         math.nan, "WAITING", time.monotonic())
        self.draw_atmosphere(width, height)
        self.draw_environment(width, height)
        self.draw_grid(width, height)
        obstacle = self.obstacle_detected(sample)
        self.draw_sensor_field(width, height, sample, obstacle)
        self.draw_person(width, height, avatar_sample)
        self.draw_minimap(width, sample, obstacle)
        self.draw_world_axes(width, height)
        c.create_text(18, 17, anchor="nw", text="INTERACTIVE 3D DIGITAL TWIN",
                      fill=self.MUTED, font=("Segoe UI Semibold", 10))
        c.create_text(18, 38, anchor="nw",
                      text=f"{self.environment_mode} WORLD  /  CAMERA yaw {self.yaw:+.0f}°  pitch {self.pitch:+.0f}°  zoom {self.zoom:.2f}x",
                      fill="#45677f", font=("Consolas", 9))
        wearer_state = "WEARER MOVING" if sample and sample.motion > 5 else (
            "WEARER STABLE" if sample else "DIGITAL TWIN / WAITING FOR IMU")
        obstacle_state = (f"OBSTACLE {sample.distance:.1f} cm" if obstacle and sample else "PATH CLEAR")
        state = f"{wearer_state} / {obstacle_state}"
        c.create_text(18, height-18, anchor="sw", text=state, fill=self.RED if obstacle and sample and sample.distance < 60 else self.GREEN,
                      font=("Segoe UI Semibold", 13))

    def draw_history(self, graph: tk.Canvas) -> None:
        graph.delete("all")
        w, h = max(graph.winfo_width(), 280), max(graph.winfo_height(), 62)
        graph.create_line(0, h/2, w, h/2, fill="#173248")
        axes = graph.axes  # type: ignore[attr-defined]
        limit = 2.0 if axes[0].startswith("a") else 180.0
        for name in axes:
            values = self.histories[name]
            points = []
            for i, value in enumerate(values):
                points.extend((i * w / (len(values)-1), h/2 - max(-limit, min(limit, value)) * (h*.42/limit)))
            graph.create_line(*points, fill=self.AXIS[name[-1]], width=2, smooth=True)

    def update_telemetry(self, s: Sample | None, fresh: bool) -> None:
        obstacle = self.obstacle_detected(s) if fresh else False
        danger = bool(obstacle and s and s.distance < 60)
        self.presence_label.configure(
            text=("OBSTACLE DANGER" if danger else "OBSTACLE DETECTED" if obstacle else "PATH CLEAR / SCANNING"),
            fg=self.RED if danger else self.AMBER if obstacle else self.GREEN)
        if not s:
            return
        for name in self.imu_labels:
            value = getattr(s, name)
            self.imu_labels[name].configure(text=f"{value:+.3f}" if name.startswith("a") else f"{value:+.1f}")
        self.distance_label.configure(text="RANGE NO ECHO" if math.isnan(s.distance) else f"RANGE {s.distance:.1f} cm")
        self.motion_label.configure(text=f"MOTION {s.motion:.1f} dps", fg=self.GREEN if s.motion > 5 else self.TEXT)
        tilt = math.degrees(math.atan2(s.ax, math.sqrt(s.ay*s.ay + s.az*s.az)))
        self.tilt_label.configure(text=f"TILT {tilt:+.1f}°")
        self.temp_label.configure(text=f"TEMP {s.temperature:.1f}°C")
        roll, pitch = self.orientation(s)
        load = math.sqrt(s.ax*s.ax + s.ay*s.ay + s.az*s.az)
        posture = "LEVEL"
        if abs(roll) > 28 or abs(pitch) > 28:
            posture = "HIGH TILT"
        elif abs(roll) > 12 or abs(pitch) > 12:
            posture = "LEANING"
        clearance = "NO ECHO" if math.isnan(s.distance) else (
            "CRITICAL" if s.distance < 60 else "CAUTION" if s.distance < 120 else "CLEAR")
        self.posture_label.configure(text=f"POSTURE {posture}",
                                     fg=self.AMBER if posture != "LEVEL" else self.GREEN)
        self.gravity_label.configure(text=f"LOAD {load:.2f} g  /  R {roll:+.0f}° P {pitch:+.0f}°")
        self.clearance_label.configure(text=f"CLEARANCE {clearance}",
                                       fg=self.RED if clearance == "CRITICAL" else
                                       self.AMBER if clearance in ("CAUTION", "NO ECHO") else self.GREEN)
        healthy = "RANGE_OK" in s.status and "IMU_OK" in s.status
        self.health_label.configure(text=("LIVE SENSORS NOMINAL" if healthy else s.status),
                                    fg=self.GREEN if healthy else self.AMBER)
        if s.received_at != self.last_history_sample:
            self.last_history_sample = s.received_at
            self.sample_times.append(s.received_at)
            for name in self.histories:
                self.histories[name].append(getattr(s, name))
            if len(self.sample_times) > 1:
                span = self.sample_times[-1] - self.sample_times[0]
                hz = (len(self.sample_times)-1) / span if span > 0 else 0.0
                self.stream_label.configure(text=f"STREAM {hz:.1f} Hz")

    def tick(self) -> None:
        self.frame_count += 1
        try:
            while True:
                kind, value = self.messages.get_nowait()
                if kind == "sample":
                    self.sample = value
                else:
                    self.connection_text = value
        except queue.Empty:
            pass
        live_fresh = bool(self.sample and time.monotonic() - self.sample.received_at < 2.0)
        if self.demo:
            shown = self.demo_sample()
            fresh = True
            connection = "DEMO DATA / LIVE PORT REMAINS CONNECTED"
        else:
            shown = self.sample if live_fresh else None
            fresh = live_fresh
            connection = self.connection_text
        self.display_sample = shown
        self.connection.configure(text=connection)
        self.status_dot.configure(fg=self.GREEN if fresh else self.AMBER)
        self.update_telemetry(shown, fresh)
        self.draw_scene(shown)
        self.draw_history(self.accel_graph)
        self.draw_history(self.gyro_graph)
        self.root.after(40, self.tick)

    def close(self) -> None:
        self.reader.stop()
        self.root.destroy()


def main() -> None:
    parser = argparse.ArgumentParser(description="NETRA interactive 3D knee-pad monitor")
    parser.add_argument("--port", default="COM6")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--demo", action="store_true", help="start with simulated live sensor data")
    args = parser.parse_args()
    root = tk.Tk()
    app = NetraApp(root, args.port, args.baud)
    if args.demo:
        app.toggle_demo()
    root.mainloop()


if __name__ == "__main__":
    main()
