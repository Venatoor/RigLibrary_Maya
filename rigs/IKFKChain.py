import maya.cmds as mc

import Utils.algorithms
from RigLibrary.base import module
from RigLibrary.base import control

from Utils import ParentOffsetMatrixTransfer


global footCtrl

global limbCtrl


def build(chainJnts, rootJoint,
          mainCtrlLocator, prefix = "chain",
          baseRig = None,
          scale = 1.0):

    rigmodule = module.Module(prefix = prefix, baseObj= baseRig)


    # Adding Control Joints
    ikChain = []
    fkChain = []

    ikCtrls = []
    fkCtrls = []

    switchAt = "IKFKSwitch"

    lengthChainJnts = len(chainJnts)
    for i in range(0, lengthChainJnts):


        jointName = Utils.algorithms.RemoveSuffix(chainJnts[i])
        jointName = jointName[:]


        ikJoint = mc.duplicate(chainJnts[i], n=prefix + "_ik_joint", parentOnly=True)[0]
        fkJoint = mc.duplicate(chainJnts[i], n=prefix + "_fk_joint", parentOnly=True)[0]

        ikChain.append(ikJoint)
        fkChain.append(fkJoint)

    # Parenting to create the chain

    for i in range ( lengthChainJnts):
        if i == 0:
            continue
        else:
            mc.parent( ikChain[i], ikChain[i-1])
            mc.parent( fkChain[i], fkChain[i-1])

        # Parenting to IK/FK Group

    mc.parent(ikChain[0], rigmodule.partsNoTransGrp)
    mc.parent(fkChain[0], rigmodule.partsNoTransGrp)

    ## i in range ( len(ikChain)):
    ##    ParentOffsetMatrixTransfer.parentOffsetTransfer(ikChain[i])
    ##for i in range ( len(fkChain)):
    ##    ParentOffsetMatrixTransfer.parentOffsetTransfer(ikChain[i])


    listOfParentConstraints = []

    for i in range(lengthChainJnts):

        parentConstraint = mc.parentConstraint( fkChain[i], ikChain[i], chainJnts[i], wal = True )
        listOfParentConstraints.append(parentConstraint[0])

    chainControl = control.Control( prefix = prefix + "root" + prefix, scale= scale * 11, translateTo= fkChain[0],
                                   rotateTo= fkChain[0] , shape = "circleZ", parentTo= rigmodule.controlsGrp, lockChanels= ["s"])

    global chainCtrl
    chainCtrl = chainControl

    #FK CONTROLS ( THERE IS A BUG HERE IF THE PREFIX HAS MULTIPLE PREFIXES WITH THE SAME NAME, THE LIMB SOLUTION IS TEMPORARY
    # UNTIL I CREATE A PARAMETER STRING WHERE TO SET THE LIMB INTOs)

    for i in range (lengthChainJnts):

        chainFKCtrl = control.Control( prefix = prefix + "_fk_limb1" + prefix, scale= scale * 10, translateTo= fkChain[i], rotateTo= fkChain[0],
                                   shape= "circleY", parentTo= rigmodule.controlsGrp, lockChanels= ["s"])
        fkCtrls.append(chainFKCtrl)

    #IK CONTROLS

    limbIkCtrl = control.Control(prefix = prefix + "_ik" + prefix, scale= scale * 14, translateTo= ikChain[-1], rotateTo= ikChain[-1],
                                 shape= "circleY", parentTo= rigmodule.controlsGrp, lockChanels= ["s"])

    ikCtrls.append(limbIkCtrl)

    # ATTRIBUTES CREATION

    reverse_node = mc.shadingNode("reverse", asUtility=True)
    ikfkSwitch = mc.addAttr(chainControl.C, ln=switchAt, at='long', minValue=0, maxValue=1, k=1)
    mc.connectAttr(chainControl.C + "." + switchAt, reverse_node + ".inputX")


    for i in range (len(fkCtrls)):

        mc.addAttr( fkCtrls[i].C, ln = switchAt, at = "long", minValue = 0, maxValue = 1, k = 1)
        mc.connectAttr( chainControl.C + "." + switchAt , fkCtrls[i].C + ".v")
        mc.connectAttr(chainControl.C + "." + switchAt, fkCtrls[i].C + "." + switchAt)

    for j in range ( len(ikCtrls)):

        mc.addAttr(ikCtrls[j].C, ln=switchAt, at="long", minValue=0, maxValue=1, k=1)
        mc.connectAttr( reverse_node + ".outputX", ikCtrls[j].C + ".v")
        mc.connectAttr( reverse_node + ".outputX", ikCtrls[j].C + "." + switchAt)

    # FK CONSTRAINTS

    blending_reverse_node = mc.shadingNode("reverse" , asUtility=True)

    mc.connectAttr(chainControl.C + "." + switchAt, blending_reverse_node + ".inputX")
    # can use either len of fkChain or ikChain same number but different objects
    for i in range(len(fkChain)):
        mc.connectAttr(chainControl.C + "." + switchAt, listOfParentConstraints[i] + ".w0")

        mc.connectAttr(blending_reverse_node + ".outputX", listOfParentConstraints[i] + ".w1")


    # FK JOINT ORIENT RESET

    for i in range(len(fkChain)):
        ParentOffsetMatrixTransfer.parentOffsetTransfer(fkChain[i])
        for axis in ["X", "Y", 'Z']:
            mc.setAttr(fkChain[i] + ".jointOrient" + axis, 0)


    #FK SETUP

    for i in range ( len(fkCtrls)):
        if i == 0 :
            mc.connectAttr( fkCtrls[i].C + ".worldMatrix[0]", fkChain[i] + ".offsetParentMatrix")
        else:
            mc.connectAttr(fkCtrls[i].C + ".translate", fkChain[i] + ".translate")
            mc.connectAttr(fkCtrls[i].C + ".rotate", fkChain[i] + ".rotate")


    #FK ROOT SETUP

    mc.connectAttr( chainControl.C + ".worldMatrix[0]", fkCtrls[0].C + ".offsetParentMatrix")

    # IK JOINT ORIENT RESET

    for i in range(len(ikChain)):
        ParentOffsetMatrixTransfer.parentOffsetTransfer(ikChain[i])
        for axis in ["X", "Y", 'Z']:
            mc.setAttr(ikChain[i] + ".jointOrient" + axis, 0)

    # IK ROOT SETUP

    mc.connectAttr( chainControl.C + ".worldMatrix[0]", ikChain[0] + ".offsetParentMatrix")


    #IK CONSTRAINTS

    limbIkHandle = mc.ikHandle( n = prefix + "_ikh", sol = "ikRPsolver", sj = ikChain[0] , ee = ikChain[-1] )[0]
    mc.parent( limbIkHandle, limbIkCtrl.C )

    return {"module":rigmodule}
