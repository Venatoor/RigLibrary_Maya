import maya.cmds as mc

import Utils.algorithms
from RigLibrary.base import module
from RigLibrary.base import control

from Utils import ParentOffsetMatrixTransfer

switchAt = "IKFKSwitch"







def build( limbJoints,
           prefix = "quadrupedalLimb",
           baseRig = None,
           scale = 1.0,
           rootJoint = "",
           PVLocator = 1.0,
           hasPaw = True,
           pawJoint = "",
           isRight = True):

    rigmodule = module.Module(prefix=prefix, baseObj=baseRig)

    ikChain = []
    fkChain = []

    ikCtrls = []
    fkCtrls = []

    limbPrefix = ""

    if (isRight):
        limbPrefix = "_r"
    else:
        limbPrefix = "_l"

    lengthLimbJoints = len(limbJoints)

    for i in range(0, lengthLimbJoints):
        jointName = Utils.algorithms.RemoveSuffix(limbJoints[i])
        jointName = jointName[:]

        ikJoint = mc.duplicate(limbJoints[i], n=limbJoints[i] + "_ik_joint", parentOnly=True)[0]
        fkJoint = mc.duplicate(limbJoints[i], n=limbJoints[i] + "_fk_joint", parentOnly=True)[0]

        ikChain.append(ikJoint)
        print(ikChain)
        fkChain.append(fkJoint)


    # Parenting to create the chain

    for i in range(lengthLimbJoints):
        if i == 0:
            continue
        else:
            mc.parent(ikChain[i], ikChain[i - 1])
            mc.parent(fkChain[i], fkChain[i - 1])

        # Parenting to IK/FK Group

    mc.parent(ikChain[0], rigmodule.partsNoTransGrp)
    mc.parent(fkChain[0], rigmodule.partsNoTransGrp)

    listOfParentConstraints = []

    for i in range(lengthLimbJoints):
        parentConstraint = mc.parentConstraint(fkChain[i], ikChain[i], limbJoints[i], wal=True)
        listOfParentConstraints.append(parentConstraint[0])

    limbControl = control.Control(prefix=prefix + "root" + limbPrefix, scale=scale * 11, translateTo=fkChain[0],
                                  rotateTo=fkChain[0], shape="circleZ", parentTo=rigmodule.controlsGrp,
                                  lockChanels=["s"])

    global limbCtrl
    limbCtrl = limbControl

    limb1FkCtrl = control.Control(prefix=prefix + "_fk_limb1" + limbPrefix, scale=scale * 10, translateTo=fkChain[0],
                                  rotateTo=fkChain[0],
                                  shape="circleY", parentTo=rigmodule.controlsGrp, lockChanels=["s"])

    limb2FkCtrl = control.Control(prefix=prefix + "_fk_limb2" + limbPrefix, scale=scale * 10, translateTo=fkChain[1],
                                  rotateTo=fkChain[1],
                                  shape="circleY", parentTo=limb1FkCtrl.C, lockChanels=["s"])

    limb3FkCtrl = control.Control(prefix=prefix + "_fk_limb3" + limbPrefix, scale=scale * 10, translateTo=fkChain[2],
                                  rotateTo=fkChain[2],
                                  shape="circleY", parentTo=limb2FkCtrl.C, lockChanels=["s"])

    fkCtrls.append(limb1FkCtrl)
    fkCtrls.append(limb2FkCtrl)
    fkCtrls.append(limb3FkCtrl)

    limbIkCtrl = control.Control(prefix=prefix + "_ik" + limbPrefix, scale=scale * 14, translateTo=ikChain[-1],
                                 rotateTo=ikChain[-1], shape="circleY", parentTo=rigmodule.controlsGrp,
                                 lockChanels=["s"])

    ikCtrls.append(limbIkCtrl)

    reverse_node = mc.shadingNode("reverse", asUtility=True)
    ikfkSwitch = mc.addAttr(limbControl.C, ln=switchAt, at='long', minValue=0, maxValue=1, k=1)
    mc.connectAttr(limbControl.C + "." + switchAt, reverse_node + ".inputX")

    for i in range(len(fkCtrls)):
        mc.addAttr(fkCtrls[i].C, ln=switchAt, at="long", minValue=0, maxValue=1, k=1)
        mc.connectAttr(limbControl.C + "." + switchAt, fkCtrls[i].C + ".v")
        mc.connectAttr(limbControl.C + "." + switchAt, fkCtrls[i].C + "." + switchAt)

    for j in range(len(ikCtrls)):
        mc.addAttr(ikCtrls[j].C, ln=switchAt, at="long", minValue=0, maxValue=1, k=1)
        mc.connectAttr(reverse_node + ".outputX", ikCtrls[j].C + ".v")
        mc.connectAttr(reverse_node + ".outputX", ikCtrls[j].C + "." + switchAt)

    # FK CONSTRAINTS

    blending_reverse_node = mc.shadingNode("reverse", asUtility=True)

    mc.connectAttr(limbControl.C + "." + switchAt, blending_reverse_node + ".inputX")
    # can use either len of fkChain or ikChain same number but different objects
    for i in range(len(fkChain)):
        mc.connectAttr(limbControl.C + "." + switchAt, listOfParentConstraints[i] + ".w0")

        mc.connectAttr(blending_reverse_node + ".outputX", listOfParentConstraints[i] + ".w1")

    # FK JOINT ORIENT RESET

    for i in range(len(fkChain)):
        ParentOffsetMatrixTransfer.parentOffsetTransfer(fkChain[i])
        for axis in ["X", "Y", 'Z']:
            mc.setAttr(fkChain[i] + ".jointOrient" + axis, 0)

    # FK SETUP

    for i in range(len(fkCtrls)):
        if i == 0:
            mc.connectAttr(fkCtrls[i].C + ".worldMatrix[0]", fkChain[i] + ".offsetParentMatrix")
        else:
            mc.connectAttr(fkCtrls[i].C + ".translate", fkChain[i] + ".translate")
            mc.connectAttr(fkCtrls[i].C + ".rotate", fkChain[i] + ".rotate")

    # FK ROOT SETUP

    mc.connectAttr(limbControl.C + ".worldMatrix[0]", fkCtrls[0].C + ".offsetParentMatrix")

    # IK JOINT ORIENT RESET

    for i in range(len(ikChain)):
        ParentOffsetMatrixTransfer.parentOffsetTransfer(ikChain[i])
        for axis in ["X", "Y", 'Z']:
            mc.setAttr(ikChain[i] + ".jointOrient" + axis, 0)

    # IK ROOT SETUP

    mc.connectAttr(limbControl.C + ".worldMatrix[0]", ikChain[0] + ".offsetParentMatrix")


    driverJoints = []
    limbJointsLength = len(limbJoints)

    for i in range(limbJointsLength):
        driverJoint = mc.duplicate(limbJoints[i], parentOnly=True, n="driver_" + prefix)[0]
        driverJoints.append(driverJoint)

    # Parenting to create the chain

    for i in range(limbJointsLength):
        if i == 0:
            continue
        else:
            mc.parent(driverJoints[i], driverJoints[i - 1])

    # =======================
    # IK PROCEDURE
    # =======================
    # Adding driver femur to the root


    mc.parent(driverJoints[0], rigmodule.partsNoTransGrp)

    # Creating a Ik Spring Solver between the joints of driver ( excluding paws ) => driver_IkHandle

    driverIkHandle = mc.ikHandle(n=prefix + "driver_ikh", sol="ikSpringSolver", sj=driverJoints[0], ee=driverJoints[-2])[0]

    # Creating a Ik RP Solver between femur and metarsus of root  => ankle_IkHandle

    ankleIkHandle = mc.ikHandle(n=prefix + "ankle_ikh", sol="ikRPsolver", sj=ikChain[0], ee=ikChain[2])[0]

    # Creating a Ik Single Chain between 2 last elements of root to create the hook => hook_IkHandle

    hookIkHandle = mc.ikHandle(n=prefix + "hook_ikh", sol="ikSCsolver", sj=ikChain[-3], ee=ikChain[-2])[0]


    mc.parent(driverIkHandle, ikCtrls[0].C)

    # Parenting ankle_IkHandle to its corresponding joint in the driver

    mc.parent(hookIkHandle, driverJoints[-2])

    # Parenting hook_IkHandle to its corresponding joint in the driver

    mc.parent(ankleIkHandle, driverJoints[2])

    # Creating toe_IkHandle with a Ik Single Chain and parenting it

    toeIkHandle = mc.ikHandle(n=prefix + "toe_ikh", sol="ikSCsolver", sj=ikChain[-2], ee=ikChain[-1])


