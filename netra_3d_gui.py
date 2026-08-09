"""NETRA true-3D wearable digital twin using PySide6 Qt3D."""

from __future__ import annotations

import argparse
import math
import queue
import sys
import time
from collections import deque

from pathlib import Path

from PySide6.QtCore import QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QPainter, QPen, QQuaternion, QVector3D
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget,
)
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6 import Qt3DCore, Qt3DExtras, Qt3DRender

QEntity = Qt3DCore.Qt3DCore.QEntity
QTransform = Qt3DCore.Qt3DCore.QTransform
QCuboidMesh = Qt3DExtras.Qt3DExtras.QCuboidMesh
QCylinderMesh = Qt3DExtras.Qt3DExtras.QCylinderMesh
QOrbitCameraController = Qt3DExtras.Qt3DExtras.QOrbitCameraController
QPhongMaterial = Qt3DExtras.Qt3DExtras.QPhongMaterial
QPlaneMesh = Qt3DExtras.Qt3DExtras.QPlaneMesh
QSphereMesh = Qt3DExtras.Qt3DExtras.QSphereMesh
Qt3DWindow = Qt3DExtras.Qt3DExtras.Qt3DWindow
QCamera = Qt3DRender.Qt3DRender.QCamera
QDirectionalLight = Qt3DRender.Qt3DRender.QDirectionalLight
QPointLight = Qt3DRender.Qt3DRender.QPointLight

from netra_gui import Sample, SerialReader


BG = "#050b14"
PANEL = "#0b1928"
TEXT = "#eaf7ff"
MUTED = "#7895aa"
CYAN = "#35d9ff"
GREEN = "#48e6a1"
AMBER = "#ffc15b"
RED = "#ff607b"
AXIS = {"x": "#ff657e", "y": "#52e7a6", "z": "#55a7ff"}


class TraceWidget(QWidget):
    def __init__(self, names: tuple[str, str, str], limit: float):
        super().__init__()
        self.names, self.limit = names, limit
        self.data = {n: deque([0.0] * 100, maxlen=100) for n in names}
        self.setMinimumHeight(70)

    def add(self, sample: Sample) -> None:
        for name in self.names:
            value = getattr(sample, name)
            self.data[name].append(0.0 if math.isnan(value) else value)
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#07121f"))
        p.setPen(QPen(QColor("#173248"), 1))
        p.drawLine(0, self.height() // 2, self.width(), self.height() // 2)
        for name in self.names:
            p.setPen(QPen(QColor(AXIS[name[-1]]), 2))
            values = list(self.data[name])
            last = None
            for i, value in enumerate(values):
                x = i * self.width() / max(1, len(values) - 1)
                y = self.height()/2 - max(-self.limit, min(self.limit, value)) * self.height()*.42/self.limit
                if last:
                    p.drawLine(int(last[0]), int(last[1]), int(x), int(y))
                last = (x, y)


class HumanRig:
    def __init__(self, root: QEntity):
        self.keep = []
        self.root = QEntity(root)
        self.root_transform = QTransform()
        self.root.addComponent(self.root_transform)
        self.skin = self.material(QColor("#c98f72"))
        self.shirt = self.material(QColor("#116f91"))
        self.trousers = self.material(QColor("#172b44"))
        self.shoe = self.material(QColor("#101820"))
        self.pad = self.material(QColor(GREEN))

        # Pelvis and shaped torso create a recognisably human silhouette.
        self.part(self.root, QCuboidMesh(), self.trousers, QVector3D(0, 1.02, 0), QVector3D(.42, .24, .24))
        self.part(self.root, QCuboidMesh(), self.shirt, QVector3D(0, 1.43, 0), QVector3D(.54, .62, .25))
        self.part(self.root, QCylinderMesh(), self.skin, QVector3D(0, 1.79, 0), QVector3D(.11, .12, .11))
        self.part(self.root, QSphereMesh(), self.skin, QVector3D(0, 1.98, 0), QVector3D(.18, .23, .18))
        # Hair cap adds depth and a less mannequin-like head.
        self.part(self.root, QSphereMesh(), self.material(QColor("#231a18")),
                  QVector3D(0, 2.08, -.015), QVector3D(.185, .12, .185))

        self.left_arm = self.limb_chain(self.root, QVector3D(-.35, 1.66, 0), .36, .34,
                                        self.shirt, self.skin, .09)
        self.right_arm = self.limb_chain(self.root, QVector3D(.35, 1.66, 0), .36, .34,
                                         self.shirt, self.skin, .09)
        self.left_leg = self.limb_chain(self.root, QVector3D(-.16, .96, 0), .48, .48,
                                        self.trousers, self.trousers, .13, foot=True)
        self.right_leg = self.limb_chain(self.root, QVector3D(.16, .96, 0), .48, .48,
                                         self.trousers, self.trousers, .13, foot=True)

        # Wearable knee pad and sensor enclosure follow the right knee joint.
        knee_parent = self.right_leg[1]
        self.part(knee_parent, QCuboidMesh(), self.pad, QVector3D(0, -.035, -.145),
                  QVector3D(.25, .22, .055))
        self.part(knee_parent, QCuboidMesh(), self.material(QColor(CYAN)),
                  QVector3D(0, -.035, -.19), QVector3D(.11, .09, .045))

    def material(self, color: QColor) -> QPhongMaterial:
        m = QPhongMaterial()
        m.setDiffuse(color)
        m.setAmbient(color.lighter(125))
        m.setSpecular(QColor("#d9f7ff"))
        m.setShininess(55.0)
        self.keep.append(m)
        return m

    def part(self, parent, mesh, material, position, scale, rotation=None):
        entity = QEntity(parent)
        if isinstance(mesh, QCylinderMesh):
            mesh.setRadius(.5)
            mesh.setLength(1.0)
            mesh.setRings(24)
            mesh.setSlices(28)
        elif isinstance(mesh, QSphereMesh):
            mesh.setRings(28)
            mesh.setSlices(32)
        transform = QTransform()
        transform.setTranslation(position)
        transform.setScale3D(scale)
        if rotation:
            transform.setRotation(rotation)
        entity.addComponent(mesh)
        entity.addComponent(material)
        entity.addComponent(transform)
        self.keep.extend((entity, mesh, material, transform))
        return entity, transform

    def limb_chain(self, parent, hip, upper_len, lower_len, upper_mat, lower_mat, radius, foot=False):
        upper_joint = QEntity(parent)
        upper_t = QTransform(); upper_t.setTranslation(hip); upper_joint.addComponent(upper_t)
        self.part(upper_joint, QCylinderMesh(), upper_mat, QVector3D(0, -upper_len/2, 0),
                  QVector3D(radius*2, upper_len, radius*2))
        knee = QEntity(upper_joint)
        knee_t = QTransform(); knee_t.setTranslation(QVector3D(0, -upper_len, 0)); knee.addComponent(knee_t)
        self.keep.extend((upper_joint, upper_t, knee, knee_t))
        self.part(knee, QSphereMesh(), lower_mat, QVector3D(0, 0, 0), QVector3D(radius*1.08, radius*.92, radius*1.08))
        self.part(knee, QCylinderMesh(), lower_mat, QVector3D(0, -lower_len/2, 0),
                  QVector3D(radius*1.72, lower_len, radius*1.72))
        if foot:
            self.part(knee, QCuboidMesh(), self.shoe, QVector3D(0, -lower_len, -.075),
                      QVector3D(radius*2.1, .10, .30))
        return upper_t, knee, knee_t

    def pose(self, phase: float, amplitude: float, tilt: float) -> None:
        swing = math.sin(phase) * (8 + 34 * amplitude)
        knee = max(0.0, math.sin(phase)) * (8 + 48 * amplitude)
        other_knee = max(0.0, -math.sin(phase)) * (8 + 48 * amplitude)
        self.left_leg[0].setRotation(QQuaternion.fromEulerAngles(swing, 0, 0))
        self.right_leg[0].setRotation(QQuaternion.fromEulerAngles(-swing, 0, 0))
        self.left_leg[2].setRotation(QQuaternion.fromEulerAngles(-other_knee, 0, 0))
        self.right_leg[2].setRotation(QQuaternion.fromEulerAngles(-knee, 0, 0))
        self.left_arm[0].setRotation(QQuaternion.fromEulerAngles(-swing*.75, 0, 5))
        self.right_arm[0].setRotation(QQuaternion.fromEulerAngles(swing*.75, 0, -5))
        self.root_transform.setRotation(QQuaternion.fromEulerAngles(0, 0, max(-10, min(10, tilt*.2))))
        self.root_transform.setTranslation(QVector3D(0, abs(math.sin(phase))*0.025*amplitude, 0))


class Netra3D(QMainWindow):
    def __init__(self, port: str, baud: int):
        super().__init__()
        self.setWindowTitle("NETRA REAL 3D | Human Walking Digital Twin")
        self.resize(1500, 900)
        self.messages: queue.Queue = queue.Queue()
        self.reader = SerialReader(port, baud, self.messages)
        self.reader.start()
        self.sample: Sample | None = None
        self.demo = False
        self.phase = 0.0
        self.last_frame = time.monotonic()
        self.walk_level = 0.0
        self.accel_activity = 0.0
        self.last_accel = (0.0, 0.0, 1.0)
        self.last_accel_mag = 1.0
        self.last_gait_sample = 0.0
        self.walk_hold_until = 0.0
        self.stable_samples = 0
        self.keep = []
        self._build_ui()
        self._build_world()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(33)

    def _build_ui(self) -> None:
        host = QWidget(); host.setStyleSheet(f"background:{BG}; color:{TEXT};")
        self.setCentralWidget(host)
        layout = QHBoxLayout(host); layout.setContentsMargins(18,18,18,18); layout.setSpacing(14)
        self.quick = QQuickWidget()
        self.quick.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.quick.setSource(QUrl.fromLocalFile(str(Path(__file__).with_name("netra_scene.qml"))))
        self.quick.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.quick, 1)
        side = QFrame(); side.setFixedWidth(355); side.setStyleSheet(f"background:{PANEL}; border-radius:8px;")
        panel = QVBoxLayout(side); panel.setContentsMargins(16,16,16,16); panel.setSpacing(9)
        title = QLabel("NETRA  /  REAL 3D"); title.setStyleSheet(f"color:{CYAN};font:700 22px 'Segoe UI';")
        panel.addWidget(title)
        sub = QLabel("HUMAN WALKING DIGITAL TWIN"); sub.setStyleSheet(f"color:{MUTED};font:10px 'Segoe UI';")
        panel.addWidget(sub)
        self.connection = QLabel("CONNECTING COM6"); panel.addWidget(self.connection)
        self.obstacle = QLabel("PATH SCANNING"); self.obstacle.setStyleSheet(f"color:{GREEN};font:700 19px 'Segoe UI';padding:10px;background:#102436;")
        panel.addWidget(self.obstacle)
        self.motion = QLabel("WEARER MOTION --"); panel.addWidget(self.motion)
        self.acc_values = self.axis_values(panel, "ACCELEROMETER / g", ("ax","ay","az"))
        self.acc_trace = TraceWidget(("ax","ay","az"), 2.0); panel.addWidget(self.acc_trace)
        self.gyr_values = self.axis_values(panel, "GYROSCOPE / °s", ("gx","gy","gz"))
        self.gyr_trace = TraceWidget(("gx","gy","gz"), 180.0); panel.addWidget(self.gyr_trace)
        self.orientation = QLabel("KNEE ORIENTATION --"); panel.addWidget(self.orientation)
        controls = QHBoxLayout()
        demo = QPushButton("DEMO"); demo.clicked.connect(self.toggle_demo); controls.addWidget(demo)
        reset = QPushButton("RESET C6"); reset.clicked.connect(self.reader.request_reset); controls.addWidget(reset)
        for b in (demo, reset):
            b.setStyleSheet(f"QPushButton{{background:#12304a;color:{TEXT};padding:8px;border:0}} QPushButton:hover{{background:{CYAN};color:{BG}}}")
        panel.addLayout(controls)
        hint = QLabel("LEFT DRAG: ORBIT  •  WHEEL: ZOOM\nIMU drives gait  •  Ultrasonic places obstacle")
        hint.setWordWrap(True); hint.setStyleSheet(f"color:{MUTED};font:9px 'Segoe UI';")
        panel.addWidget(hint); panel.addStretch()
        layout.addWidget(side)

    def axis_values(self, parent, title, names):
        label = QLabel(title); label.setStyleSheet(f"color:{MUTED};font:700 10px 'Segoe UI';margin-top:7px")
        parent.addWidget(label)
        row = QHBoxLayout(); result = {}
        for name in names:
            item = QLabel(f"{name[-1].upper()}  --")
            item.setStyleSheet(f"color:{AXIS[name[-1]]};font:700 13px Consolas;background:#07121f;padding:7px")
            row.addWidget(item); result[name] = item
        parent.addLayout(row)
        return result

    def material(self, color):
        base = QColor(color)
        m = QPhongMaterial(); m.setDiffuse(base); m.setAmbient(base.lighter(125)); m.setSpecular(QColor("#bdeeff")); m.setShininess(35)
        self.keep.append(m)
        return m

    def entity(self, mesh, material, position, scale, rotation=None):
        e = QEntity(self.root); t = QTransform(); t.setTranslation(position); t.setScale3D(scale)
        if rotation: t.setRotation(rotation)
        e.addComponent(mesh); e.addComponent(material); e.addComponent(t)
        self.keep.extend((e, mesh, material, t))
        return e, t

    def _build_world(self) -> None:
        self.qml_root = self.quick.rootObject()
        if self.qml_root is None:
            details = "\n".join(str(e) for e in self.quick.errors())
            raise RuntimeError(f"Qt Quick 3D scene failed to load:\n{details}")
        return

    def _build_legacy_world(self) -> None:
        self.root = QEntity()
        floor = QPlaneMesh(); floor.setWidth(16); floor.setHeight(16); floor.setMeshResolution(QSize(2, 2))
        self.entity(floor, self.material("#172a33"), QVector3D(0,0,0), QVector3D(1,1,1), QQuaternion.fromEulerAngles(-90,0,0))
        # Environmental markers provide strong parallax and spatial context.
        for x,z,h in ((-3,-2,1.4),(3,-3,2.1),(-4,1,1.8),(4,2,1.2)):
            self.entity(QCylinderMesh(), self.material("#244b3a"), QVector3D(x,h/2,z), QVector3D(.18,h,.18))
            self.entity(QSphereMesh(), self.material("#2e7650"), QVector3D(x,h+.35,z), QVector3D(.58,.70,.58))
        self.human = HumanRig(self.root)
        obstacle_mesh = QCuboidMesh()
        self.obstacle_entity, self.obstacle_transform = self.entity(
            obstacle_mesh, self.material(AMBER), QVector3D(0,.5,-3), QVector3D(1.1,1.0,.7))
        beam_mesh = QCylinderMesh(); beam_mesh.setRadius(.012); beam_mesh.setLength(1.0)
        self.beam_entity, self.beam_transform = self.entity(
            beam_mesh, self.material(CYAN), QVector3D(.16,.58,-1.5), QVector3D(1,3,1),
            QQuaternion.fromEulerAngles(90,0,0))
        light_e = QEntity(self.root); light = QDirectionalLight(); light.setColor(QColor("#e8f7ff")); light.setIntensity(1.0)
        light.setWorldDirection(QVector3D(-1,-2,-1)); light_e.addComponent(light)
        fill_e = QEntity(self.root); fill = QPointLight(); fill.setColor(QColor(CYAN)); fill.setIntensity(.45)
        fill_t = QTransform(); fill_t.setTranslation(QVector3D(2,3,2)); fill_e.addComponent(fill); fill_e.addComponent(fill_t)
        camera: QCamera = self.view.camera(); camera.lens().setPerspectiveProjection(45,16/9,.1,100)
        camera.setPosition(QVector3D(4.2,2.7,5.5)); camera.setViewCenter(QVector3D(0,1,-.5)); camera.setUpVector(QVector3D(0,1,0))
        orbit = QOrbitCameraController(self.root); orbit.setCamera(camera); orbit.setLinearSpeed(5); orbit.setLookSpeed(120)
        self.keep.extend((light_e, light, fill_e, fill, fill_t, orbit))
        self.view.setRootEntity(self.root)

    def toggle_demo(self):
        self.demo = not self.demo

    def demo_sample(self) -> Sample:
        t=time.monotonic()
        return Sample(90+40*math.sin(t*.35), .12*math.sin(t*2), .05, 1.0,
                      18*math.cos(t*2), 55*math.sin(t*2), 9*math.sin(t), 29.2,
                      "RANGE_OK|IMU_OK", time.monotonic())

    def tick(self) -> None:
        try:
            while True:
                kind,value=self.messages.get_nowait()
                if kind=="sample": self.sample=value
                else: self.connection.setText(str(value))
        except queue.Empty:
            pass
        fresh=bool(self.sample and time.monotonic()-self.sample.received_at<2)
        s=self.demo_sample() if self.demo else self.sample if fresh else None
        dt=min(.08,time.monotonic()-self.last_frame); self.last_frame=time.monotonic()
        # Walking comes from accelerometer dynamics, not gyro magnitude. Remove
        # the static 1 g gravity vector, combine it with sample-to-sample change,
        # and smooth the result so the rig walks naturally instead of jittering.
        if s and s.received_at != self.last_gait_sample:
            self.last_gait_sample = s.received_at
            values = (s.ax, s.ay, s.az)
            if all(not math.isnan(v) for v in values):
                accel_mag = math.sqrt(sum(v*v for v in values))
                magnitude_change = abs(accel_mag - self.last_accel_mag)
                delta = math.sqrt(sum((v-p)*(v-p) for v,p in zip(values, self.last_accel)))
                # Vector change detects leg rotation; magnitude change detects
                # step impact. Both ignore the sensor's constant calibration bias.
                self.accel_activity = 0.72*delta + 0.28*magnitude_change
                target = max(0.0, min(1.0, (self.accel_activity - 0.008) * 13.0))
                if target > .10:
                    self.walk_hold_until = time.monotonic() + .85
                    self.stable_samples = 0
                elif self.accel_activity < .006:
                    self.stable_samples += 1
                    if self.stable_samples >= 2:
                        self.walk_hold_until = 0.0
                        self.walk_level *= .25
                else:
                    self.stable_samples = 0
                self.walk_level = self.walk_level*0.58 + target*0.42
                self.last_accel = values
                self.last_accel_mag = accel_mag
        elif not s:
            self.walk_level *= 0.94
        if self.demo:
            self.walk_level = max(self.walk_level, 0.68)
        elif time.monotonic() < self.walk_hold_until:
            self.walk_level = max(self.walk_level, 0.28)
        gait = self.walk_level
        self.phase += dt*(2.8+gait*6.5) if gait>.035 or self.demo else 0
        tilt=math.degrees(math.atan2(s.ax,math.sqrt(s.ay*s.ay+s.az*s.az))) if s else 0
        self.qml_root.setProperty("gaitPhase", self.phase)
        self.qml_root.setProperty("gaitAmount", gait)
        self.qml_root.setProperty("bodyTilt", tilt)
        obstacle_ok=bool(s and "RANGE_OK" in s.status and not math.isnan(s.distance) and 2<=s.distance<=250)
        self.qml_root.setProperty("obstacleVisible", obstacle_ok)
        if obstacle_ok:
            z=max(45.0,min(360.0,s.distance)); self.qml_root.setProperty("obstacleZ", z)
            danger=s.distance<60; self.obstacle.setText(("DANGER" if danger else "OBSTACLE")+f"  {s.distance:.1f} cm")
            self.obstacle.setStyleSheet(f"color:{RED if danger else AMBER};font:700 19px 'Segoe UI';padding:10px;background:#102436")
        else:
            self.obstacle.setText("PATH CLEAR / SCANNING")
        if s:
            for name,label in {**self.acc_values,**self.gyr_values}.items():
                label.setText(f"{name[-1].upper()} {getattr(s,name):+.2f}")
            gait_state = "WALKING" if gait > .08 else "STANDING"
            self.motion.setText(f"{gait_state}  •  ACCEL ACTIVITY {self.accel_activity:.3f} g")
            self.orientation.setText(f"KNEE TILT  {tilt:+.1f}°  /  TEMP {s.temperature:.1f}°C")
            self.acc_trace.add(s); self.gyr_trace.add(s)

    def closeEvent(self, event):
        self.reader.stop(); event.accept()


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--port",default="COM6"); parser.add_argument("--baud",type=int,default=115200)
    args=parser.parse_args(); app=QApplication(sys.argv); app.setStyle("Fusion")
    window=Netra3D(args.port,args.baud); window.show(); sys.exit(app.exec())


if __name__ == "__main__":
    main()
