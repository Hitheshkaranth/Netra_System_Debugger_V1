import QtQuick
import QtQuick3D
import "assets/cesium_man/generated"

Rectangle {
    id: root
    color: "#07131f"
    property real gaitPhase: 0
    property real gaitAmount: 0
    property real bodyTilt: 0
    property real obstacleZ: -180
    property real obstacleX: 0
    property real sensorX: 18
    property real beamLength: Math.sqrt(obstacleZ*obstacleZ + (obstacleX-sensorX)*(obstacleX-sensorX))
    property real beamAngle: Math.atan2(obstacleX-sensorX, obstacleZ) * 180 / Math.PI
    property bool obstacleVisible: false
    property real worldYaw: -18

    View3D {
        anchors.fill: parent
        environment: SceneEnvironment {
            clearColor: "#07131f"
            backgroundMode: SceneEnvironment.Color
            antialiasingMode: SceneEnvironment.MSAA
            antialiasingQuality: SceneEnvironment.High
        }

        PerspectiveCamera {
            id: camera
            position: Qt.vector3d(0, 125, 520)
            eulerRotation.x: -7
            clipFar: 2000
        }
        DirectionalLight { eulerRotation: Qt.vector3d(-35, -25, 0); brightness: .72; castsShadow: true }
        PointLight { position: Qt.vector3d(220, 300, 240); color: "#52dfff"; brightness: 4 }

        Node {
            id: world
            eulerRotation.y: root.worldYaw

            Model {
                source: "#Cube"
                position: Qt.vector3d(0, -4, -60)
                scale: Qt.vector3d(8, .05, 8)
                materials: PrincipledMaterial { baseColor: "#18343a"; roughness: .82 }
                castsShadows: false
            }

            // Indoor rehabilitation/safety corridor shell.
            Model { source:"#Cube"; position:Qt.vector3d(-310,135,-70); scale:Qt.vector3d(.10,2.7,8); materials:wall }
            Model { source:"#Cube"; position:Qt.vector3d(310,135,-70); scale:Qt.vector3d(.10,2.7,8); materials:wall }
            Model { source:"#Cube"; position:Qt.vector3d(0,275,-70); scale:Qt.vector3d(6.2,.10,8); materials:ceiling }
            Model { source:"#Cube"; position:Qt.vector3d(0,135,-860); scale:Qt.vector3d(6.2,2.7,.10); materials:wallDark }
            // Indoor vinyl floor tiles and architectural trim.
            Repeater3D {
                model: 32
                Model {
                    property int col: index % 4
                    property int row: Math.floor(index / 4)
                    source:"#Cube"
                    position:Qt.vector3d((col-1.5)*150,1,-600+row*150)
                    scale:Qt.vector3d(1.48,.012,1.48)
                    materials: (col+row)%2===0 ? floorTileA : floorTileB
                }
            }
            Model { source:"#Cube"; position:Qt.vector3d(-300,12,-70); scale:Qt.vector3d(.08,.20,8); materials:baseboard }
            Model { source:"#Cube"; position:Qt.vector3d(300,12,-70); scale:Qt.vector3d(.08,.20,8); materials:baseboard }
            Model { source:"#Cube"; position:Qt.vector3d(0,260,-70); scale:Qt.vector3d(6.1,.06,.055); materials:ceilingTrim }
            // Ceiling tile seams add indoor scale and depth.
            Repeater3D {
                model: 7
                Model { source:"#Cube"; position:Qt.vector3d(-300+index*100,268,-70); scale:Qt.vector3d(.012,.018,8); materials:ceilingSeam }
            }
            Repeater3D {
                model: 9
                Model { source:"#Cube"; position:Qt.vector3d(0,268,-670+index*150); scale:Qt.vector3d(6,.018,.012); materials:ceilingSeam }
            }
            // Wall panels, doors, rails, benches and ceiling luminaires.
            Repeater3D {
                model: 6
                Node {
                    property real side: index % 2 === 0 ? -1 : 1
                    property real row: Math.floor(index/2)
                    position:Qt.vector3d(side*303,135,-360+row*250)
                    Model { source:"#Cube"; scale:Qt.vector3d(.025,1.45,.72); materials:wallPanel }
                    Model { source:"#Cube"; position:Qt.vector3d(-side*7,-60,0); scale:Qt.vector3d(.035,.035,.72); materials:rail }
                    Model { source:"#Sphere"; position:Qt.vector3d(-side*11,-60,0); scale:Qt.vector3d(.045,.045,.045); materials:rail }
                }
            }
            Repeater3D {
                model: 5
                Node {
                    position:Qt.vector3d(0,267,-460+index*180)
                    Model { source:"#Cube"; scale:Qt.vector3d(1.05,.025,.24); materials:ceilingLight }
                    PointLight { position.y:-8; color:"#d8f7ff"; brightness:3 }
                }
            }
            Model { source:"#Cube"; position:Qt.vector3d(-255,36,-180); scale:Qt.vector3d(.72,.09,.32); materials:bench }
            Model { source:"#Cube"; position:Qt.vector3d(-280,18,-180); scale:Qt.vector3d(.08,.36,.28); materials:benchDark }
            Model { source:"#Cube"; position:Qt.vector3d(255,36,-430); scale:Qt.vector3d(.72,.09,.32); materials:bench }
            Model { source:"#Cube"; position:Qt.vector3d(280,18,-430); scale:Qt.vector3d(.08,.36,.28); materials:benchDark }
            Model { source:"#Cube"; position:Qt.vector3d(-303,115,120); scale:Qt.vector3d(.03,1.8,.58); materials:door }
            Model { source:"#Sphere"; position:Qt.vector3d(-292,108,145); scale:Qt.vector3d(.04,.04,.04); materials:handle }
            // Observation window and clinical equipment.
            Model { source:"#Cube"; position:Qt.vector3d(0,150,-848); scale:Qt.vector3d(3.35,1.35,.025); materials:observationGlass }
            Model { source:"#Cube"; position:Qt.vector3d(0,150,-842); scale:Qt.vector3d(3.55,.045,.035); materials:windowFrame }
            Model { source:"#Cube"; position:Qt.vector3d(0,82,-842); scale:Qt.vector3d(3.55,.045,.035); materials:windowFrame }
            Model { source:"#Cube"; position:Qt.vector3d(0,218,-842); scale:Qt.vector3d(3.55,.045,.035); materials:windowFrame }
            Model { source:"#Cube"; position:Qt.vector3d(-175,150,-842); scale:Qt.vector3d(.045,1.4,.035); materials:windowFrame }
            Model { source:"#Cube"; position:Qt.vector3d(175,150,-842); scale:Qt.vector3d(.045,1.4,.035); materials:windowFrame }
            // Reception/work counter, diagnostic monitor, equipment cart.
            Model { source:"#Cube"; position:Qt.vector3d(-235,50,-545); scale:Qt.vector3d(1.15,1,.48); materials:counter }
            Model { source:"#Cube"; position:Qt.vector3d(-235,107,-545); scale:Qt.vector3d(1.25,.12,.55); materials:counterTop }
            Model { source:"#Cube"; position:Qt.vector3d(-300,168,-420); scale:Qt.vector3d(.03,.78,.85); materials:monitor }
            Model { source:"#Cube"; position:Qt.vector3d(-292,168,-420); scale:Qt.vector3d(.025,.65,.72); materials:monitorScreen }
            Node { position:Qt.vector3d(245,0,-250)
                Model { source:"#Cube"; position.y:46; scale:Qt.vector3d(.72,.08,.45); materials:cart }
                Model { source:"#Cube"; position.y:88; scale:Qt.vector3d(.72,.08,.45); materials:cart }
                Model { source:"#Cylinder"; position:Qt.vector3d(-28,23,-16); scale:Qt.vector3d(.035,.46,.035); materials:rail }
                Model { source:"#Cylinder"; position:Qt.vector3d(28,23,-16); scale:Qt.vector3d(.035,.46,.035); materials:rail }
                Model { source:"#Sphere"; position:Qt.vector3d(-28,5,-16); scale:Qt.vector3d(.07,.07,.07); materials:wheel }
                Model { source:"#Sphere"; position:Qt.vector3d(28,5,-16); scale:Qt.vector3d(.07,.07,.07); materials:wheel }
            }
            // Potted indoor plant and emergency equipment.
            Node { position:Qt.vector3d(260,0,-650)
                Model { source:"#Cylinder"; position.y:25; scale:Qt.vector3d(.30,.50,.30); materials:plantPot }
                Model { source:"#Cylinder"; position.y:72; scale:Qt.vector3d(.05,.55,.05); materials:plantStem }
                Model { source:"#Sphere"; position:Qt.vector3d(-16,108,0); scale:Qt.vector3d(.30,.42,.22); materials:plantLeaf }
                Model { source:"#Sphere"; position:Qt.vector3d(18,118,4); scale:Qt.vector3d(.28,.46,.22); materials:plantLeafLight }
            }
            Model { source:"#Cylinder"; position:Qt.vector3d(294,62,80); scale:Qt.vector3d(.12,.55,.12); materials:extinguisher }
            Model { source:"#Cube"; position:Qt.vector3d(0,238,-844); scale:Qt.vector3d(.75,.26,.035); materials:exitSign }

            // Walking lane, center markers, and curb edges.
            Model { source:"#Cube"; position:Qt.vector3d(0,.5,-180); scale:Qt.vector3d(2.3,.012,6.6); materials:road }
            Repeater3D {
                model: 7
                Model { source:"#Cube"; position:Qt.vector3d(0,1,-430+index*120); scale:Qt.vector3d(.035,.014,.42); materials:laneMark }
            }
            Model { source:"#Cube"; position:Qt.vector3d(-235,3,-180); scale:Qt.vector3d(.08,.06,6.6); materials:curb }
            Model { source:"#Cube"; position:Qt.vector3d(235,3,-180); scale:Qt.vector3d(.08,.06,6.6); materials:curb }

            // Ground lane and spatial markers create visible depth/parallax.
            Repeater3D {
                model: 9
                Model {
                    source: "#Cube"
                    position: Qt.vector3d((index - 4) * 100, 0, -60)
                    scale: Qt.vector3d(.012, .012, 8)
                    materials: PrincipledMaterial { baseColor: "#28505c"; emissiveFactor: Qt.vector3d(.04,.10,.12) }
                }
            }
            Repeater3D {
                model: 9
                Model {
                    source: "#Cube"
                    position: Qt.vector3d(0, 0, (index - 4) * 100 - 60)
                    scale: Qt.vector3d(8, .012, .012)
                    materials: PrincipledMaterial { baseColor: "#28505c" }
                }
            }

            // Environmental trees/buildings.
            Repeater3D {
                model: 6
                visible: false
                Node {
                    property real side: index % 2 === 0 ? -1 : 1
                    position: Qt.vector3d(side * (250 + (index % 3)*70), 0, -240 + index*85)
                    Model { source: "#Cylinder"; position.y: 55; scale: Qt.vector3d(.16,1.1,.16); materials: PrincipledMaterial { baseColor: "#5b3b25" } }
                    Model { source: "#Sphere"; position.y: 145; scale: Qt.vector3d(.7,.9,.7); materials: PrincipledMaterial { baseColor: "#28704b"; roughness: .9 } }
                }
            }
            Repeater3D {
                model: 10
                visible: false
                Node {
                    property real side: index % 2 === 0 ? -1 : 1
                    position: Qt.vector3d(side*(185+(index%3)*22), 8, -360+index*72)
                    Model { source:"#Sphere"; scale:Qt.vector3d(.28,.22,.28); materials:bush }
                    Model { source:"#Sphere"; position:Qt.vector3d(side*18,5,8); scale:Qt.vector3d(.19,.16,.2); materials:bushLight }
                }
            }
            // Illuminated safety posts make obstacle depth easier to read.
            Repeater3D {
                model: 4
                visible: false
                Node {
                    property real side: index % 2 === 0 ? -1 : 1
                    position: Qt.vector3d(side*210,0,-300+Math.floor(index/2)*260)
                    Model { source:"#Cylinder"; position.y:55; scale:Qt.vector3d(.035,1.1,.035); materials:post }
                    Model { source:"#Sphere"; position.y:114; scale:Qt.vector3d(.11,.11,.11); materials:lamp }
                    PointLight { position.y:110; color:"#72e7ff"; brightness:5 }
                }
            }

            Node {
                id: human
                visible: false
                eulerRotation.z: root.bodyTilt * .2
                eulerRotation.y: Math.sin(root.gaitPhase) * 2.5 * root.gaitAmount
                position.y: Math.abs(Math.sin(root.gaitPhase)) * 3 * root.gaitAmount

                Model { source: "#Sphere"; position.y: 103; scale: Qt.vector3d(.25,.16,.17); materials: clothDark }
                Model { source: "#Cube"; position.y: 121; scale: Qt.vector3d(.40,.28,.22); materials: shirtDark }
                Model { source: "#Cube"; position.y: 148; scale: Qt.vector3d(.54,.34,.26); materials: shirt }
                Model { source: "#Sphere"; position.y: 163; scale: Qt.vector3d(.30,.13,.17); materials: shirt }
                Model { source: "#Cube"; position:Qt.vector3d(0,148,14); scale:Qt.vector3d(.025,.30,.012); materials:zipper }
                Model { source: "#Cylinder"; position.y: 179; scale: Qt.vector3d(.11,.12,.11); materials: skin }
                Model { source: "#Sphere"; position.y: 199; scale: Qt.vector3d(.18,.23,.18); materials: skin }
                Model { source: "#Sphere"; position: Qt.vector3d(0,209,-2); scale: Qt.vector3d(.185,.12,.185); materials: hair }
                // Face: ears, eyes, nose, eyebrows and mouth.
                Model { source:"#Sphere"; position:Qt.vector3d(-18,200,1); scale:Qt.vector3d(.035,.07,.04); materials:skin }
                Model { source:"#Sphere"; position:Qt.vector3d(18,200,1); scale:Qt.vector3d(.035,.07,.04); materials:skin }
                Model { source:"#Sphere"; position:Qt.vector3d(-6.5,204,16); scale:Qt.vector3d(.026,.018,.014); materials:eyeWhite }
                Model { source:"#Sphere"; position:Qt.vector3d(6.5,204,16); scale:Qt.vector3d(.026,.018,.014); materials:eyeWhite }
                Model { source:"#Sphere"; position:Qt.vector3d(-6.5,204,17.4); scale:Qt.vector3d(.010,.010,.007); materials:eye }
                Model { source:"#Sphere"; position:Qt.vector3d(6.5,204,17.4); scale:Qt.vector3d(.010,.010,.007); materials:eye }
                Model { source:"#Cone"; position:Qt.vector3d(0,198,20); eulerRotation.x:90; scale:Qt.vector3d(.035,.085,.035); materials:skin }
                Model { source:"#Cube"; position:Qt.vector3d(0,190,17); scale:Qt.vector3d(.055,.009,.01); materials:mouth }

                // Arms counter-swing with the legs.
                Node {
                    position: Qt.vector3d(-35,166,0)
                    eulerRotation.x: -Math.sin(root.gaitPhase) * (12 + 35*root.gaitAmount)
                    eulerRotation.z: 5
                    Model { source:"#Sphere"; scale:Qt.vector3d(.12,.12,.12); materials:shirt }
                    Model { source:"#Cylinder"; position.y:-18; scale:Qt.vector3d(.09,.36,.09); materials:shirt }
                    Node { position.y:-36; eulerRotation.x: -12
                        Model { source:"#Sphere"; scale:Qt.vector3d(.085,.085,.085); materials:skin }
                        Model { source:"#Cylinder"; position.y:-17; scale:Qt.vector3d(.075,.34,.075); materials:skin }
                        Model { source:"#Sphere"; position.y:-35; scale:Qt.vector3d(.09,.12,.08); materials:skin }
                    }
                }
                Node {
                    position: Qt.vector3d(35,166,0)
                    eulerRotation.x: Math.sin(root.gaitPhase) * (12 + 35*root.gaitAmount)
                    eulerRotation.z: -5
                    Model { source:"#Sphere"; scale:Qt.vector3d(.12,.12,.12); materials:shirt }
                    Model { source:"#Cylinder"; position.y:-18; scale:Qt.vector3d(.09,.36,.09); materials:shirt }
                    Node { position.y:-36; eulerRotation.x: -12
                        Model { source:"#Sphere"; scale:Qt.vector3d(.085,.085,.085); materials:skin }
                        Model { source:"#Cylinder"; position.y:-17; scale:Qt.vector3d(.075,.34,.075); materials:skin }
                        Model { source:"#Sphere"; position.y:-35; scale:Qt.vector3d(.09,.12,.08); materials:skin }
                    }
                }

                Node {
                    id: leftHip
                    position: Qt.vector3d(-16,96,0)
                    eulerRotation.x: Math.sin(root.gaitPhase) * (8 + 40*root.gaitAmount)
                    Model { source:"#Sphere"; scale:Qt.vector3d(.15,.14,.15); materials:clothDark }
                    Model { source:"#Cylinder"; position.y:-24; scale:Qt.vector3d(.13,.48,.13); materials:clothDark }
                    Node { position.y:-48; eulerRotation.x: -Math.max(0,-Math.sin(root.gaitPhase))*(10+55*root.gaitAmount)
                        Model { source:"#Sphere"; scale:Qt.vector3d(.14,.12,.14); materials:clothDark }
                        Model { source:"#Cylinder"; position.y:-24; scale:Qt.vector3d(.11,.48,.11); materials:clothDark }
                        Model { source:"#Sphere"; position.y:-47; scale:Qt.vector3d(.10,.08,.10); materials:skinDark }
                        Model { source:"#Cube"; position:Qt.vector3d(0,-49,-8); scale:Qt.vector3d(.26,.10,.35); materials:shoe }
                        Model { source:"#Cube"; position:Qt.vector3d(0,-48,-20); scale:Qt.vector3d(.23,.025,.12); materials:sole }
                    }
                }
                Node {
                    id: rightHip
                    position: Qt.vector3d(16,96,0)
                    eulerRotation.x: -Math.sin(root.gaitPhase) * (8 + 40*root.gaitAmount)
                    Model { source:"#Sphere"; scale:Qt.vector3d(.15,.14,.15); materials:clothDark }
                    Model { source:"#Cylinder"; position.y:-24; scale:Qt.vector3d(.13,.48,.13); materials:clothDark }
                    Node {
                        id: rightKnee
                        position.y:-48
                        eulerRotation.x: -Math.max(0,Math.sin(root.gaitPhase))*(10+55*root.gaitAmount)
                        Model { source:"#Sphere"; scale:Qt.vector3d(.14,.12,.14); materials:clothDark }
                        Model { source:"#Cylinder"; position.y:-24; scale:Qt.vector3d(.11,.48,.11); materials:clothDark }
                        Model { source:"#Sphere"; position.y:-47; scale:Qt.vector3d(.10,.08,.10); materials:skinDark }
                        Model { source:"#Cube"; position:Qt.vector3d(0,-49,-8); scale:Qt.vector3d(.26,.10,.35); materials:shoe }
                        Model { source:"#Cube"; position:Qt.vector3d(0,-48,-20); scale:Qt.vector3d(.23,.025,.12); materials:sole }
                        // Layered wearable: straps, impact shell, controller and status LED.
                        Model { source:"#Cube"; position:Qt.vector3d(0,-10,13); scale:Qt.vector3d(.31,.035,.035); materials:strap }
                        Model { source:"#Cube"; position:Qt.vector3d(0,7,13); scale:Qt.vector3d(.31,.035,.035); materials:strap }
                        Model { source:"#Cube"; position:Qt.vector3d(0,-2,15); scale:Qt.vector3d(.25,.23,.06); materials:kneePad }
                        Model { source:"#Cube"; position:Qt.vector3d(0,-2,21); scale:Qt.vector3d(.11,.10,.05); materials:sensor }
                        Model { source:"#Sphere"; position:Qt.vector3d(0,0,27); scale:Qt.vector3d(.018,.018,.012); materials:led }
                    }
                }
            }

            // Textured, skinned human. Balsam exposes its skeletal walk as a
            // controllable timeline, driven here from the live IMU gait phase.
            CesiumMan {
                id: realisticHuman
                scale: Qt.vector3d(160,160,160)
                eulerRotation.y: 0
                animationFrame: (root.gaitPhase % 6.283185) / 6.283185 * 2000
                position.y: Math.abs(Math.sin(root.gaitPhase))*2*root.gaitAmount
                eulerRotation.z: root.bodyTilt*.15
            }
            // Knee wearable follows the right-leg arc and faces the same +Z
            // direction as the human face.
            Node {
                id: realisticKneePad
                position:Qt.vector3d(root.sensorX + Math.sin(root.gaitPhase)*12*root.gaitAmount,
                                     68 + Math.max(0,Math.sin(root.gaitPhase))*8*root.gaitAmount,
                                     24)
                eulerRotation.x:-Math.max(0,Math.sin(root.gaitPhase))*35*root.gaitAmount
                Model { source:"#Cube"; scale:Qt.vector3d(.30,.035,.035); position.y:-9; materials:strap }
                Model { source:"#Cube"; scale:Qt.vector3d(.30,.035,.035); position.y:9; materials:strap }
                Model { source:"#Cube"; scale:Qt.vector3d(.24,.23,.055); position.z:4; materials:kneePad }
                Model { source:"#Cube"; scale:Qt.vector3d(.105,.095,.045); position.z:10; materials:sensor }
                Model { source:"#Sphere"; scale:Qt.vector3d(.018,.018,.012); position:Qt.vector3d(0,0,15); materials:led }
            }

            // Ultrasonic beam and detected obstacle exist separately from wearer motion.
            Model {
                visible: root.obstacleVisible
                source: "#Cylinder"
                position: Qt.vector3d((root.sensorX+root.obstacleX)/2, 66, root.obstacleZ/2)
                eulerRotation.x: 90
                eulerRotation.y: root.beamAngle
                scale: Qt.vector3d(.018, root.beamLength/100, .018)
                materials: PrincipledMaterial { baseColor: "#35d9ff"; emissiveFactor: Qt.vector3d(0,.7,1) }
            }
            Model {
                visible: root.obstacleVisible
                source: "#Cone"
                position: Qt.vector3d((root.sensorX+root.obstacleX)/2,66,root.obstacleZ/2)
                eulerRotation.x: 90
                eulerRotation.y: root.beamAngle
                scale: Qt.vector3d(.42,root.beamLength/100,.42)
                materials: PrincipledMaterial {
                    baseColor: "#224bd9ff"; alphaMode: PrincipledMaterial.Blend
                    opacity: .16; emissiveFactor: Qt.vector3d(0,.12,.18)
                }
            }
            Model {
                visible: root.obstacleVisible
                source: "#Cube"
                position: Qt.vector3d(root.obstacleX, 50, root.obstacleZ)
                scale: Qt.vector3d(1.05,1,.65)
                materials: PrincipledMaterial {
                    baseColor: root.obstacleZ < 60 ? "#ff405f" : "#ffb52e"
                    metalness: .1; roughness: .45
                }
            }
            Model {
                visible: root.obstacleVisible
                source:"#Sphere"
                position:Qt.vector3d(root.obstacleX,115,root.obstacleZ)
                scale:Qt.vector3d(.12,.12,.12)
                materials:warningBeacon
            }
        }
    }

    PrincipledMaterial { id: skin; baseColor:"#c98f72"; roughness:.68 }
    PrincipledMaterial { id: shirt; baseColor:"#087ea4"; roughness:.55 }
    PrincipledMaterial { id: shirtDark; baseColor:"#075873"; roughness:.68 }
    PrincipledMaterial { id: clothDark; baseColor:"#172b44"; roughness:.8 }
    PrincipledMaterial { id: skinDark; baseColor:"#a96f56"; roughness:.75 }
    PrincipledMaterial { id: shoe; baseColor:"#101820"; roughness:.72 }
    PrincipledMaterial { id: sole; baseColor:"#557080"; roughness:.88 }
    PrincipledMaterial { id: hair; baseColor:"#231a18"; roughness:.9 }
    PrincipledMaterial { id: eyeWhite; baseColor:"#f4fbff"; roughness:.3 }
    PrincipledMaterial { id: eye; baseColor:"#17212a"; roughness:.2 }
    PrincipledMaterial { id: mouth; baseColor:"#773d3d"; roughness:.8 }
    PrincipledMaterial { id: zipper; baseColor:"#b9d7df"; metalness:.7; roughness:.25 }
    PrincipledMaterial { id: kneePad; baseColor:"#19dfa3"; metalness:.1; roughness:.35 }
    PrincipledMaterial { id: sensor; baseColor:"#35d9ff"; emissiveFactor:Qt.vector3d(0,.55,.8) }
    PrincipledMaterial { id: strap; baseColor:"#10272c"; roughness:.85 }
    PrincipledMaterial { id: led; baseColor:"#d7fff4"; emissiveFactor:Qt.vector3d(0,1,.55) }
    PrincipledMaterial { id: road; baseColor:"#24363e"; roughness:.92 }
    PrincipledMaterial { id: laneMark; baseColor:"#d2e5e8"; emissiveFactor:Qt.vector3d(.18,.2,.2) }
    PrincipledMaterial { id: curb; baseColor:"#60737a"; roughness:.8 }
    PrincipledMaterial { id: bush; baseColor:"#1e6544"; roughness:.95 }
    PrincipledMaterial { id: bushLight; baseColor:"#33845b"; roughness:.9 }
    PrincipledMaterial { id: post; baseColor:"#2a4351"; metalness:.45; roughness:.45 }
    PrincipledMaterial { id: lamp; baseColor:"#baf4ff"; emissiveFactor:Qt.vector3d(.3,1,1) }
    PrincipledMaterial { id: warningBeacon; baseColor:"#ff365c"; emissiveFactor:Qt.vector3d(1,.05,.12) }
    PrincipledMaterial { id: wall; baseColor:"#8fa4aa"; roughness:.82 }
    PrincipledMaterial { id: wallDark; baseColor:"#50666e"; roughness:.88 }
    PrincipledMaterial { id: ceiling; baseColor:"#aebdc0"; roughness:.9 }
    PrincipledMaterial { id: wallPanel; baseColor:"#718991"; roughness:.72 }
    PrincipledMaterial { id: rail; baseColor:"#6b7f86"; metalness:.8; roughness:.25 }
    PrincipledMaterial { id: ceilingLight; baseColor:"#eaffff"; emissiveFactor:Qt.vector3d(.7,1,1) }
    PrincipledMaterial { id: bench; baseColor:"#287d88"; roughness:.68 }
    PrincipledMaterial { id: benchDark; baseColor:"#1b4d58"; roughness:.72 }
    PrincipledMaterial { id: door; baseColor:"#3c6670"; roughness:.72 }
    PrincipledMaterial { id: handle; baseColor:"#d5e7e9"; metalness:.9; roughness:.18 }
    PrincipledMaterial { id: floorTileA; baseColor:"#536f78"; roughness:.83 }
    PrincipledMaterial { id: floorTileB; baseColor:"#49656e"; roughness:.86 }
    PrincipledMaterial { id: baseboard; baseColor:"#324a52"; roughness:.72 }
    PrincipledMaterial { id: ceilingTrim; baseColor:"#768b91"; roughness:.8 }
    PrincipledMaterial { id: ceilingSeam; baseColor:"#6d8085"; roughness:.88 }
    PrincipledMaterial { id: observationGlass; baseColor:"#244856"; opacity:.72; alphaMode:PrincipledMaterial.Blend; metalness:.15; roughness:.2 }
    PrincipledMaterial { id: windowFrame; baseColor:"#1c3038"; metalness:.6; roughness:.34 }
    PrincipledMaterial { id: counter; baseColor:"#316d76"; roughness:.68 }
    PrincipledMaterial { id: counterTop; baseColor:"#b9c9cb"; roughness:.38 }
    PrincipledMaterial { id: monitor; baseColor:"#17252b"; roughness:.58 }
    PrincipledMaterial { id: monitorScreen; baseColor:"#163d50"; emissiveFactor:Qt.vector3d(0,.28,.42); roughness:.22 }
    PrincipledMaterial { id: cart; baseColor:"#668891"; metalness:.45; roughness:.38 }
    PrincipledMaterial { id: wheel; baseColor:"#151d20"; roughness:.9 }
    PrincipledMaterial { id: plantPot; baseColor:"#765343"; roughness:.9 }
    PrincipledMaterial { id: plantStem; baseColor:"#326345"; roughness:.9 }
    PrincipledMaterial { id: plantLeaf; baseColor:"#2b7650"; roughness:.92 }
    PrincipledMaterial { id: plantLeafLight; baseColor:"#3c9365"; roughness:.9 }
    PrincipledMaterial { id: extinguisher; baseColor:"#d63342"; metalness:.2; roughness:.42 }
    PrincipledMaterial { id: exitSign; baseColor:"#39ff91"; emissiveFactor:Qt.vector3d(0,1,.3); roughness:.3 }

    MouseArea {
        anchors.fill: parent
        property real lastX
        onPressed: mouse => lastX = mouse.x
        onPositionChanged: mouse => { if (pressed) { root.worldYaw += (mouse.x-lastX)*.25; lastX=mouse.x } }
        onWheel: wheel => camera.z = Math.max(330, Math.min(800, camera.z - wheel.angleDelta.y*.35))
    }

    Column {
        anchors.left: parent.left; anchors.top: parent.top; anchors.margins: 22; spacing: 4
        Text { text:"WEARER DIGITAL TWIN"; color:"#eaf7ff"; font.pixelSize:18; font.bold:true }
        Text { text:"INDOOR GAIT & OBSTACLE SAFETY LAB"; color:"#52dfff"; font.pixelSize:10; font.letterSpacing:1.5 }
    }
}
