import maya.cmds as mc

import Utils.algorithms
from RigLibrary.base import module
from RigLibrary.base import control

from Utils import ParentOffsetMatrixTransfer


global footCtrl

global limbCtrl

global IsLeg

def build(limbJoints, rootJoint,
          mainCtrlLocator, prefix = "limb", isRight = False,
          baseRig = None, ikPVlocator = "",
          scale = 1.0, isLeg = False):

    #TODO : add  a
    rigmodule = module.Module(prefix = prefix, baseObj= baseRig)

    global IsLeg
    IsLeg = isLeg

    # Adding Control Joints

    limbPrefix = ""

    if ( isRight):
        limbPrefix = "_r_"
    else:
        limbPrefix = "_l_"

    ikChain = []
    fkChain = []

    ikCtrls = []
    fkCtrls = []

    switchAt = "IKFKSwitch"

    lengthLimbJoints = len(limbJoints)
    for i in range(0, lengthLimbJoints):


        jointName = Utils.algorithms.RemoveSuffix(limbJoints[i])
        jointName = jointName[:]


        ikJoint = mc.duplicate(limbJoints[i], n=prefix + "_ik_joint", parentOnly=True)[0]
        fkJoint = mc.duplicate(limbJoints[i], n=prefix + "_fk_joint", parentOnly=True)[0]

        ikChain.append(ikJoint)
        fkChain.append(fkJoint)

    # Parenting to create the chain

    for i in range ( lengthLimbJoints):
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

    for i in range(lengthLimbJoints):

        parentConstraint = mc.parentConstraint( fkChain[i], ikChain[i], limbJoints[i], wal = True )
        listOfParentConstraints.append(parentConstraint[0])

    limbControl = control.Control( prefix = prefix + "root" + limbPrefix, scale= scale * 11, translateTo= fkChain[0],
                                   rotateTo= fkChain[0] , shape = "circleZ", parentTo= rigmodule.controlsGrp, lockChanels= ["s"])

    global limbCtrl
    limbCtrl = limbControl

    #FK CONTROLS ( THERE IS A BUG HERE IF THE PREFIX HAS MULTIPLE PREFIXES WITH THE SAME NAME, THE LIMB SOLUTION IS TEMPORARY
    # UNTIL I CREATE A PARAMETER STRING WHERE TO SET THE LIMB INTOs)

    limb1FkCtrl = control.Control( prefix = prefix + "_fk_limb1" + limbPrefix, scale= scale * 10, translateTo= fkChain[0], rotateTo= fkChain[0],
                                   shape= "circleY", parentTo= rigmodule.controlsGrp, lockChanels= ["s"])

    limb2FkCtrl = control.Control( prefix = prefix + "_fk_limb2" + limbPrefix, scale= scale * 10, translateTo= fkChain[1], rotateTo= fkChain[1],
                                   shape= "circleY", parentTo= limb1FkCtrl.C, lockChanels= ["s"])

    limb3FkCtrl = control.Control( prefix = prefix + "_fk_limb3" + limbPrefix, scale= scale * 10, translateTo= fkChain[2], rotateTo= fkChain[2],
                                   shape= "circleY", parentTo= limb2FkCtrl.C, lockChanels= ["s"])

    if ( isLeg ) :
        global footCtrl
        footCtrl = limb3FkCtrl

    fkCtrls.append(limb1FkCtrl)
    fkCtrls.append(limb2FkCtrl)
    fkCtrls.append(limb3FkCtrl)

    #IK CONTROLS

    limbIkCtrl = control.Control(prefix = prefix + "_ik" + limbPrefix, scale= scale * 14, translateTo= ikChain[-1], rotateTo= ikChain[-1],
                                 shape= "circleY", parentTo= rigmodule.controlsGrp, lockChanels= ["s"])

    ikCtrls.append(limbIkCtrl)

    # ATTRIBUTES CREATION

    reverse_node = mc.shadingNode("reverse", asUtility=True)
    ikfkSwitch = mc.addAttr(limbControl.C, ln=switchAt, at='long', minValue=0, maxValue=1, k=1)
    mc.connectAttr(limbControl.C + "." + switchAt, reverse_node + ".inputX")


    for i in range (len(fkCtrls)):

        mc.addAttr( fkCtrls[i].C, ln = switchAt, at = "long", minValue = 0, maxValue = 1, k = 1)
        mc.connectAttr( limbControl.C + "." + switchAt , fkCtrls[i].C + ".v")
        mc.connectAttr(limbControl.C + "." + switchAt, fkCtrls[i].C + "." + switchAt)

    for j in range ( len(ikCtrls)):

        mc.addAttr(ikCtrls[j].C, ln=switchAt, at="long", minValue=0, maxValue=1, k=1)
        mc.connectAttr( reverse_node + ".outputX", ikCtrls[j].C + ".v")
        mc.connectAttr( reverse_node + ".outputX", ikCtrls[j].C + "." + switchAt)

    # FK CONSTRAINTS

    blending_reverse_node = mc.shadingNode("reverse" , asUtility=True)

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


    #FK SETUP

    for i in range ( len(fkCtrls)):
        if i == 0 :
            mc.connectAttr( fkCtrls[i].C + ".worldMatrix[0]", fkChain[i] + ".offsetParentMatrix")
        else:
            mc.connectAttr(fkCtrls[i].C + ".translate", fkChain[i] + ".translate")
            mc.connectAttr(fkCtrls[i].C + ".rotate", fkChain[i] + ".rotate")


    #FK ROOT SETUP

    mc.connectAttr( limbControl.C + ".worldMatrix[0]", fkCtrls[0].C + ".offsetParentMatrix")

    # IK JOINT ORIENT RESET

    for i in range(len(ikChain)):
        ParentOffsetMatrixTransfer.parentOffsetTransfer(ikChain[i])
        for axis in ["X", "Y", 'Z']:
            mc.setAttr(ikChain[i] + ".jointOrient" + axis, 0)

    # IK ROOT SETUP

    mc.connectAttr( limbControl.C + ".worldMatrix[0]", ikChain[0] + ".offsetParentMatrix")


    #IK CONSTRAINTS

    limbIkHandle = mc.ikHandle( n = prefix + "_ikh", sol = "ikRPsolver", sj = ikChain[0] , ee = ikChain[-1] )[0]
    mc.parent( limbIkHandle, limbIkCtrl.C )

    #PV CREATION

    mc.poleVectorConstraint( ikPVlocator, limbIkHandle, weight = 1.0, name = prefix + "_ik_PV" )

    #Making Arm follow Spine

    if ( isLeg == False ):

        if isRight == True :

            shoulder_ik_grp = mc.ls("shoulder_r_ik_wspace")[0]
            shoulder_fk_grp = mc.ls("shoulder_r_fk_wspace")[0]
        else :
            shoulder_ik_grp = mc.ls("shoulder_l_ik_wspace")[0]
            shoulder_fk_grp = mc.ls("shoulder_l_fk_wspace")[0]


        matrix_root_t = mc.xform(limbCtrl.C, query = True, worldSpace = True, translation = True)
        matrix_root_r = mc.xform(limbCtrl.C, query = True, worldSpace = True, rotation = True, euler = True)
        matrix_root_s = mc.xform(limbCtrl.C, query=True, worldSpace=True, scale=True)

        mc.xform(shoulder_fk_grp, worldSpace = True, translation = matrix_root_t, rotation = matrix_root_r, scale = matrix_root_s )
        mc.xform(shoulder_ik_grp, worldSpace=True, translation=matrix_root_t, rotation=matrix_root_r,
                     scale=matrix_root_s)

        blend_matrix_node = mc.shadingNode('blendMatrix', asUtility=True)

        mc.connectAttr(shoulder_fk_grp + ".worldMatrix[0]", blend_matrix_node + ".inputMatrix")
        mc.connectAttr(shoulder_ik_grp + ".worldMatrix[0]", blend_matrix_node + ".target[0].targetMatrix")

        mc.connectAttr(limbControl.C + "." + switchAt, blend_matrix_node + ".envelope")


    #matching position










    return {"module":rigmodule}
