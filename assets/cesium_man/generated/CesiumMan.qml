import QtQuick
import QtQuick3D

import QtQuick.Timeline

Node {
    id: node
    property alias animationFrame: timeline0.currentFrame

    // Resources
    property url textureData: "maps/textureData.jpg"
    Texture {
        id: _0_texture
        minFilter: Texture.Nearest
        generateMipmaps: true
        mipFilter: Texture.Linear
        source: node.textureData
    }
    PrincipledMaterial {
        id: cesium_Man_effect_material
        objectName: "Cesium_Man-effect"
        baseColorMap: _0_texture
        roughness: 1
        alphaMode: PrincipledMaterial.Opaque
    }
    Skin {
        id: skin
        joints: [
            skeleton_torso_joint_1,
            skeleton_torso_joint_2,
            torso_joint_3,
            skeleton_neck_joint_1,
            skeleton_neck_joint_2,
            skeleton_arm_joint_L__4_,
            skeleton_arm_joint_R,
            skeleton_arm_joint_L__3_,
            skeleton_arm_joint_R__2_,
            skeleton_arm_joint_L__2_,
            skeleton_arm_joint_R__3_,
            leg_joint_L_1,
            leg_joint_R_1,
            leg_joint_L_2,
            leg_joint_R_2,
            leg_joint_L_3,
            leg_joint_R_3,
            leg_joint_L_5,
            leg_joint_R_5
        ]
        inverseBindPoses: [
            Qt.matrix4x4(0.997142, 4.35865e-08, -0.075553, 0.0513005, -4.37114e-08, 1, 0, -0.00499982, 0.075553, 3.30253e-09, 0.997142, -0.677059, 0, 0, 0, 1),
            Qt.matrix4x4(0.0604175, 2.64093e-09, -0.998173, 0.82183, -4.37114e-08, 1, 0, -0.0049864, 0.998173, 4.36316e-08, 0.0604175, -0.0607639, 0, 0, 0, 1),
            Qt.matrix4x4(0.986261, 4.31108e-08, -0.165197, 0.181581, -4.37114e-08, 1, 0, -0.00498706, 0.165197, 7.22097e-09, 0.986261, -1.0586, 0, 0, 0, 1),
            Qt.matrix4x4(-0.0384785, -1.68195e-09, -0.99926, 1.13741, -4.37114e-08, 1, 0, -0.00498944, 0.99926, 4.3679e-08, -0.0384785, 0.0372934, 0, 0, 0, 1),
            Qt.matrix4x4(-0.0112752, -4.92856e-10, 0.999937, -1.18983, -4.37114e-08, 1, 0, -0.00498944, -0.999937, -4.37086e-08, -0.0112752, 0.0219168, 0, 0, 0, 1),
            Qt.matrix4x4(-0.999909, -4.37074e-08, -0.0135046, 0.0102479, -4.37114e-08, 1, 0, -0.0960007, 0.0135046, 5.90303e-10, -0.999909, 1.07396, 0, 0, 0, 1),
            Qt.matrix4x4(-0.906658, -3.96313e-08, 0.421866, -0.456943, -4.37114e-08, 1, 0, 0.0860006, -0.421866, -1.84403e-08, -0.906658, 0.971955, 0, 0, 0, 1),
            Qt.matrix4x4(-0.991697, -4.33485e-08, 0.128597, -0.139899, -4.37114e-08, 1, 0, -0.3115, -0.128597, -5.62116e-09, -0.991697, 0.954434, 0, 0, 0, 1),
            Qt.matrix4x4(0.88511, 3.86894e-08, 0.465383, -0.4347, -4.37114e-08, 1, 0, 0.3015, -0.465383, -2.03425e-08, 0.88511, -0.861135, 0, 0, 0, 1),
            Qt.matrix4x4(-0.984893, -4.3051e-08, 0.173165, -0.0860243, -4.37114e-08, 1, 0, -0.4545, -0.173165, -7.5693e-09, -0.984893, 0.873296, 0, 0, 0, 1),
            Qt.matrix4x4(0.303943, 1.32858e-08, 0.95269, -0.853817, -4.37114e-08, 1, 0, 0.444501, -0.95269, -4.16434e-08, 0.303943, -0.202596, 0, 0, 0, 1),
            Qt.matrix4x4(0.740573, 3.23715e-08, -0.671976, 0.395099, -4.37114e-08, 1, 0, -0.0730393, 0.671976, 2.9373e-08, 0.740573, -0.470674, 0, 0, 0, 1),
            Qt.matrix4x4(-0.0273315, -1.1947e-09, -0.999627, 0.614483, -4.37114e-08, 1, 0, 0.0630393, 0.999627, 4.36951e-08, -0.0273315, -0.00692671, 0, 0, 0, 1),
            Qt.matrix4x4(-0.27823, -1.21618e-08, -0.960515, 0.35694, -4.37114e-08, 1, 0, -0.0820948, 0.960515, 4.19854e-08, -0.27823, 0.0323927, 0, 0, 0, 1),
            Qt.matrix4x4(-0.214169, -9.36164e-09, -0.976797, 0.358309, -4.37114e-08, 1, 0, 0.0720653, 0.976797, 4.26971e-08, -0.214169, 0.00870073, 0, 0, 0, 1),
            Qt.matrix4x4(-0.766446, -3.35024e-08, 0.642309, -0.0586245, -4.37114e-08, 1, 0, -0.083492, -0.642309, -2.80762e-08, -0.766446, 0.0628311, 0, 0, 0, 1),
            Qt.matrix4x4(-0.737183, -3.22233e-08, 0.675693, -0.0613229, -4.37114e-08, 1, 0, 0.073497, -0.675693, -2.95355e-08, -0.737183, 0.060195, 0, 0, 0, 1),
            Qt.matrix4x4(-0.998158, -4.36309e-08, 0.0606729, 0.0255387, -4.37114e-08, 1, 0, -0.0845827, -0.0606729, -2.6521e-09, -0.998158, 0.0228279, 0, 0, 0, 1),
            Qt.matrix4x4(-0.997126, -4.35858e-08, 0.0757577, 0.025234, -4.37114e-08, 1, 0, 0.0745693, -0.0757577, -3.31148e-09, -0.997126, 0.0232133, 0, 0, 0, 1)
        ]
    }

    // Nodes:
    Node {
        id: z_UP
        objectName: "Z_UP"
        rotation: Qt.quaternion(0.707107, -0.707107, 0, 0)
        Node {
            id: armature
            objectName: "Armature"
            rotation: Qt.quaternion(0.707107, 0, 0, -0.707107)
            Node {
                id: skeleton_torso_joint_1
                objectName: "Skeleton_torso_joint_1"
                position: Qt.vector3d(1.57554e-08, 0.00499984, 0.679)
                rotation: Qt.quaternion(0.999285, 0, 0.0378035, 0)
                Node {
                    id: skeleton_torso_joint_2
                    objectName: "Skeleton_torso_joint_2"
                    position: Qt.vector3d(1.33617e-05, -1.33738e-05, 0.145417)
                    rotation: Qt.quaternion(0.753545, 0, 0.657396, 0)
                    scale: Qt.vector3d(1, 1, 1)
                    Node {
                        id: torso_joint_3
                        objectName: "torso_joint_3"
                        position: Qt.vector3d(-0.250517, 6.07222e-07, -7.29081e-05)
                        rotation: Qt.quaternion(0.782458, 0, -0.622703, 0)
                        Node {
                            id: skeleton_neck_joint_1
                            objectName: "Skeleton_neck_joint_1"
                            position: Qt.vector3d(-2.36603e-06, 2.41399e-06, 0.0648362)
                            rotation: Qt.quaternion(0.750708, 0, 0.660635, 0)
                            scale: Qt.vector3d(1, 1, 1)
                            Node {
                                id: skeleton_neck_joint_2
                                objectName: "Skeleton_neck_joint_2"
                                position: Qt.vector3d(-0.0520402, -3.39933e-08, -2.66079e-06)
                                rotation: Qt.quaternion(0.0248792, 0, 0.99969, 0)
                                scale: Qt.vector3d(1, 1, 1)
                            }
                        }
                        Node {
                            id: skeleton_arm_joint_L__4_
                            objectName: "Skeleton_arm_joint_L__4_"
                            position: Qt.vector3d(-3.83747e-05, 0.0910136, -6.14334e-05)
                            rotation: Qt.quaternion(0.0896108, 0, 0.995977, 0)
                            Node {
                                id: skeleton_arm_joint_L__3_
                                objectName: "Skeleton_arm_joint_L__3_"
                                position: Qt.vector3d(0.0132216, 0.2155, 0.109332)
                                rotation: Qt.quaternion(0.997464, 0, 0.0711694, 0)
                                Node {
                                    id: skeleton_arm_joint_L__2_
                                    objectName: "Skeleton_arm_joint_L__2_"
                                    position: Qt.vector3d(-0.0933246, 0.143, 0.0781479)
                                    rotation: Qt.quaternion(0.999746, 0, 0.0225422, 0)
                                    scale: Qt.vector3d(1, 1, 1)
                                }
                            }
                        }
                        Node {
                            id: skeleton_arm_joint_R
                            objectName: "Skeleton_arm_joint_R"
                            position: Qt.vector3d(-3.83025e-05, -0.0909877, -6.20323e-05)
                            rotation: Qt.quaternion(-0.134365, 0, 0.990932, 0)
                            Node {
                                id: skeleton_arm_joint_R__2_
                                objectName: "Skeleton_arm_joint_R__2_"
                                position: Qt.vector3d(-0.0355463, -0.215499, 0.104233)
                                rotation: Qt.quaternion(0.443755, 0, 0.896148, 0)
                                scale: Qt.vector3d(1, 1, 1)
                                Node {
                                    id: skeleton_arm_joint_R__3_
                                    objectName: "Skeleton_arm_joint_R__3_"
                                    position: Qt.vector3d(0.0313702, -0.143001, -0.117612)
                                    rotation: Qt.quaternion(0.925308, 0, -0.379217, 0)
                                    scale: Qt.vector3d(1, 1, 1)
                                }
                            }
                        }
                    }
                }
                Node {
                    id: leg_joint_L_1
                    objectName: "leg_joint_L_1"
                    position: Qt.vector3d(0.02852, 0.0680394, -0.0629594)
                    rotation: Qt.quaternion(0.94584, 0, 0.324634, 0)
                    Node {
                        id: leg_joint_L_2
                        objectName: "leg_joint_L_2"
                        position: Qt.vector3d(0.209164, 0.0090555, -0.16427)
                        rotation: Qt.quaternion(0.848349, 0, 0.529437, 0)
                        scale: Qt.vector3d(1, 1, 1)
                        Node {
                            id: leg_joint_L_3
                            objectName: "leg_joint_L_3"
                            position: Qt.vector3d(0.27579, 0.00139725, 0.00412248)
                            rotation: Qt.quaternion(0.546031, 0, 0.837765, 0)
                            scale: Qt.vector3d(1, 1, 1)
                            Node {
                                id: leg_joint_L_5
                                objectName: "leg_joint_L_5"
                                position: Qt.vector3d(-0.0655838, 0.00109065, 0.0292915)
                                rotation: Qt.quaternion(0.949738, 0, -0.313046, 0)
                            }
                        }
                    }
                }
                Node {
                    id: leg_joint_R_1
                    objectName: "leg_joint_R_1"
                    position: Qt.vector3d(0.0285572, -0.0680391, -0.0629586)
                    rotation: Qt.quaternion(0.723972, 0, 0.689829, 0)
                    Node {
                        id: leg_joint_R_2
                        objectName: "leg_joint_R_2"
                        position: Qt.vector3d(0.260891, -0.00902605, 0.0516709)
                        rotation: Qt.quaternion(0.995561, 0, 0.0941138, 0)
                        scale: Qt.vector3d(1, 1, 1)
                        Node {
                            id: leg_joint_R_3
                            objectName: "leg_joint_R_3"
                            position: Qt.vector3d(0.27546, -0.00143173, -0.0141048)
                            rotation: Qt.quaternion(0.498933, 0, 0.866641, 0)
                            Node {
                                id: leg_joint_R_5
                                objectName: "leg_joint_R_5"
                                position: Qt.vector3d(-0.0668196, -0.00107226, 0.0263513)
                                rotation: Qt.quaternion(0.945054, 0, -0.326915, 0)
                            }
                        }
                    }
                }
            }
            Model {
                id: cesium_Man
                objectName: "Cesium_Man"
                source: "meshes/cesium_Man_mesh.mesh"
                skin: skin
                materials: [
                    cesium_Man_effect_material
                ]
            }
        }
    }

    // Animations:
    Timeline {
        id: timeline0
        enabled: true
        objectName: "timeline0"
        property real framesPerSecond: 1000
        startFrame: 0
        endFrame: 2000
        currentFrame: 0
        KeyframeGroup {
            target: skeleton_arm_joint_L__2_
            property: "rotation"
            keyframeSource: "animations/skeleton_arm_joint_L__2__rotation_0.qad"
        }
        KeyframeGroup {
            target: skeleton_torso_joint_1
            property: "position"
            keyframeSource: "animations/skeleton_torso_joint_1_position_0.qad"
        }
        KeyframeGroup {
            target: skeleton_torso_joint_1
            property: "rotation"
            keyframeSource: "animations/skeleton_torso_joint_1_rotation_0.qad"
        }
        KeyframeGroup {
            target: skeleton_neck_joint_1
            property: "position"
            keyframeSource: "animations/skeleton_neck_joint_1_position_0.qad"
        }
        KeyframeGroup {
            target: skeleton_neck_joint_1
            property: "rotation"
            keyframeSource: "animations/skeleton_neck_joint_1_rotation_0.qad"
        }
        KeyframeGroup {
            target: skeleton_torso_joint_2
            property: "position"
            keyframeSource: "animations/skeleton_torso_joint_2_position_0.qad"
        }
        KeyframeGroup {
            target: skeleton_torso_joint_2
            property: "rotation"
            keyframeSource: "animations/skeleton_torso_joint_2_rotation_0.qad"
        }
        KeyframeGroup {
            target: skeleton_neck_joint_2
            property: "position"
            keyframeSource: "animations/skeleton_neck_joint_2_position_0.qad"
        }
        KeyframeGroup {
            target: skeleton_neck_joint_2
            property: "rotation"
            keyframeSource: "animations/skeleton_neck_joint_2_rotation_0.qad"
        }
        KeyframeGroup {
            target: torso_joint_3
            property: "position"
            keyframeSource: "animations/torso_joint_3_position_0.qad"
        }
        KeyframeGroup {
            target: torso_joint_3
            property: "rotation"
            keyframeSource: "animations/torso_joint_3_rotation_0.qad"
        }
        KeyframeGroup {
            target: skeleton_arm_joint_L__4_
            property: "position"
            keyframeSource: "animations/skeleton_arm_joint_L__4__position_0.qad"
        }
        KeyframeGroup {
            target: skeleton_arm_joint_L__4_
            property: "rotation"
            keyframeSource: "animations/skeleton_arm_joint_L__4__rotation_0.qad"
        }
        KeyframeGroup {
            target: skeleton_arm_joint_L__3_
            property: "position"
            keyframeSource: "animations/skeleton_arm_joint_L__3__position_0.qad"
        }
        KeyframeGroup {
            target: skeleton_arm_joint_L__3_
            property: "rotation"
            keyframeSource: "animations/skeleton_arm_joint_L__3__rotation_0.qad"
        }
        KeyframeGroup {
            target: skeleton_arm_joint_R
            property: "position"
            keyframeSource: "animations/skeleton_arm_joint_R_position_0.qad"
        }
        KeyframeGroup {
            target: skeleton_arm_joint_R
            property: "rotation"
            keyframeSource: "animations/skeleton_arm_joint_R_rotation_0.qad"
        }
        KeyframeGroup {
            target: skeleton_arm_joint_R__2_
            property: "rotation"
            keyframeSource: "animations/skeleton_arm_joint_R__2__rotation_0.qad"
        }
        KeyframeGroup {
            target: skeleton_arm_joint_R__3_
            property: "rotation"
            keyframeSource: "animations/skeleton_arm_joint_R__3__rotation_0.qad"
        }
        KeyframeGroup {
            target: leg_joint_L_1
            property: "position"
            Keyframe {
                frame: 41.6666
                value: Qt.vector3d(0.0285201, 0.0676218, -0.0629599)
            }
        }
        KeyframeGroup {
            target: leg_joint_L_1
            property: "rotation"
            keyframeSource: "animations/leg_joint_L_1_rotation_0.qad"
        }
        KeyframeGroup {
            target: leg_joint_L_2
            property: "rotation"
            keyframeSource: "animations/leg_joint_L_2_rotation_0.qad"
        }
        KeyframeGroup {
            target: leg_joint_L_3
            property: "position"
            keyframeSource: "animations/leg_joint_L_3_position_0.qad"
        }
        KeyframeGroup {
            target: leg_joint_L_3
            property: "rotation"
            keyframeSource: "animations/leg_joint_L_3_rotation_0.qad"
        }
        KeyframeGroup {
            target: leg_joint_L_5
            property: "position"
            keyframeSource: "animations/leg_joint_L_5_position_0.qad"
        }
        KeyframeGroup {
            target: leg_joint_L_5
            property: "rotation"
            keyframeSource: "animations/leg_joint_L_5_rotation_0.qad"
        }
        KeyframeGroup {
            target: leg_joint_R_1
            property: "position"
            Keyframe {
                frame: 41.6666
                value: Qt.vector3d(0.0285572, -0.0684543, -0.0629587)
            }
        }
        KeyframeGroup {
            target: leg_joint_R_1
            property: "rotation"
            keyframeSource: "animations/leg_joint_R_1_rotation_0.qad"
        }
        KeyframeGroup {
            target: leg_joint_R_2
            property: "rotation"
            keyframeSource: "animations/leg_joint_R_2_rotation_0.qad"
        }
        KeyframeGroup {
            target: leg_joint_R_3
            property: "position"
            keyframeSource: "animations/leg_joint_R_3_position_0.qad"
        }
        KeyframeGroup {
            target: leg_joint_R_3
            property: "rotation"
            keyframeSource: "animations/leg_joint_R_3_rotation_0.qad"
        }
        KeyframeGroup {
            target: leg_joint_R_5
            property: "position"
            keyframeSource: "animations/leg_joint_R_5_position_0.qad"
        }
        KeyframeGroup {
            target: leg_joint_R_5
            property: "rotation"
            keyframeSource: "animations/leg_joint_R_5_rotation_0.qad"
        }
    }

    // An exported mapping of Timelines (--manualAnimations)
    property var timelineMap: {
        "timeline0": timeline0,
    }
    // A simple list of Timelines (--manualAnimations)
    property var timelineList: [
        timeline0,
    ]
}
