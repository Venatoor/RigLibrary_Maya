import maya.cmds as mc

import Utils.algorithms
from RigLibrary.base import module
from RigLibrary.base import control

from Utils import ParentOffsetMatrixTransfer

#PARAMETERES OF THE SPINE

ikChain = []
fkChain = []

ikCtrls = []
fkCtrls = []

twistJoints= []

global cogCtrl

switchAt = "IKFKSwitch"

reverseNodePrefix = "Spine_IK_FK_Reverse"

# GETTERS and SETTERS

def GetIkChain():
    return ikChain

def GetFkChain():
    return fkChain

def GetSwitch():
    return switchAt

def GetIkCtrls():
    return ikCtrls

def GetFkCtrls():
    return fkCtrls


def build(spineJoints,
          spineCurve,
          spineRootJoint,
          hipsLocator,
          prefix = "spine",
          baseRig = None,
          spineScale = 1.0
          ):


    #Will also require curve + locators for IK/FK specific locations

    rigmodule = module.Module(prefix= prefix, baseObj= baseRig)

    #Adding Control Joints



    lengthSpineJoints = len(spineJoints)
    for i in range( 0, lengthSpineJoints):

        prefix = Utils.algorithms.RemoveSuffix(spineJoints[i])
        prefix = prefix[:]

        ikJoint = mc.duplicate( spineJoints[i], n = prefix + "_ik_joint", parentOnly = True )[0]
        fkJoint = mc.duplicate( spineJoints[i], n = prefix + "_fk_joint", parentOnly = True )[0]

        ikChain.append(ikJoint)
        fkChain.append(fkJoint)


    #Parenting to create the chain

    for i in range ( lengthSpineJoints):
        if i == 0:
            continue
        else:
            mc.parent( ikChain[i], ikChain[i-1])
            mc.parent( fkChain[i], fkChain[i-1])

    #Parenting to IK/FK Group

    mc.parent( ikChain[0], rigmodule.partsNoTransGrp)
    mc.parent( fkChain[0], rigmodule.partsNoTransGrp)


    #Parent constraint

    listOfParentConstraints = []

    for i in range(lengthSpineJoints):

        parentConstraint = mc.parentConstraint( fkChain[i], ikChain[i], spineJoints[i], wal = True )
        listOfParentConstraints.append(parentConstraint[0])
        ##print(mc.getAttr(parentConstraint[0] + ".w1"))


    #Creation of controls

    global cogCtrl
    cogCtrl = control.Control( prefix = prefix + "fk_cog", scale = spineScale * 35,
                               translateTo= spineJoints[0], rotateTo= spineJoints[0],
                               shape= "circleY", parentTo= rigmodule.controlsGrp)

    #FK CONTROLS


    ## THIS SECTION IS TEMP AND BADLY WRITTEN SHOULD BE GENERALISED AND MORE MODULAR

    # can be generalised and looped ( WIP )
    pelvisCtrl = control.Control(prefix=prefix + "fk_pelvis", scale=spineScale * 24,
                                 translateTo=spineJoints[0], rotateTo=spineJoints[0],
                                 shape="circleY", parentTo=cogCtrl.C, lockChanels= ["s"])
    spine1Ctrl = control.Control(prefix=prefix + "fk_spine1", scale=spineScale * 24,
                                 translateTo=spineJoints[1], rotateTo=spineJoints[1],
                                 shape="circleY", parentTo=pelvisCtrl.C, lockChanels= ["s"])



    spine2Ctrl = control.Control(prefix=prefix + "fk_spine2", scale=spineScale * 24,
                                 translateTo=spineJoints[2], rotateTo=spineJoints[2],
                                 shape="circleY", parentTo=spine1Ctrl.C, lockChanels= ["s"])


    spine3Ctrl = control.Control(prefix=prefix + "fk_spine3", scale=spineScale * 24,
                                translateTo=spineJoints[3], rotateTo=spineJoints[3],
                                shape="circleY", parentTo=spine2Ctrl.C, lockChanels= ["s"])


    fkCtrls.append(pelvisCtrl)
    fkCtrls.append(spine1Ctrl)
    fkCtrls.append(spine2Ctrl)
    fkCtrls.append(spine3Ctrl)



    #IK CONTROLS

    #can be generalised and looped ( WIP )

    hipsCtrl = control.Control( prefix=prefix + "ik_hips", scale = spineScale * 24,
                                translateTo= hipsLocator, rotateTo= hipsLocator,
                                shape = "circleY", parentTo= cogCtrl.C, lockChanels= ["s"])

    lowerSpineCtrl = control.Control( prefix = prefix + "ik_lowerSpine", scale= spineScale * 24,
                                      translateTo= spineJoints[0], rotateTo= spineJoints[0],
                                      shape= "circleY", parentTo= cogCtrl.C, lockChanels= ["s"])
    twistJoints.append(mc.duplicate(spineJoints[0], n="ik_lowerSpine" + "_Twist1_Jnt", parentOnly=True)[0])

    chestCtrl = control.Control( prefix = prefix + "ik_chest", scale= spineScale * 24,
                                 translateTo= spineJoints[2], rotateTo= spineJoints[2],
                                 shape= "circleY", parentTo= lowerSpineCtrl.C, lockChanels= ["s"])
    twistJoints.append(mc.duplicate(spineJoints[2], n="ik_chest" + "_Twist1_Jnt", parentOnly=True)[0])

    shoulderCtrl = control.Control( prefix = prefix + "ik_shoulder", scale= spineScale * 24,
                                    translateTo= spineJoints[4], rotateTo= spineJoints[4],
                                    shape = "circleY", parentTo= chestCtrl.C, lockChanels= ["s"])
    twistJoints.append(mc.duplicate(spineJoints[4], n="ik_shoulder" + "_Twist1_Jnt", parentOnly=True)[0])

    for i in range ( len(twistJoints) ):
        mc.setAttr(twistJoints[i] + ".radius", 10)
        mc.parent(twistJoints[i], rigmodule.jointsGrp)
        ParentOffsetMatrixTransfer.parentOffsetTransfer(twistJoints[i])


    ikCtrls.append(hipsCtrl)
    ikCtrls.append(lowerSpineCtrl)
    ikCtrls.append(chestCtrl)
    ikCtrls.append(shoulderCtrl)

    ##################################################################################################

    #Attributes Creation

    # Attribute of IKFK Switch is created in Cog and linked to fk ctrls and ik ctrls

    reverse_node = mc.shadingNode("reverse", asUtility=True)
    ikfkSwitch = mc.addAttr( cogCtrl.C, ln = switchAt, at = 'long', minValue = 0, maxValue = 1, k = 1 )
    mc.connectAttr( cogCtrl.C + "." + switchAt, reverse_node + ".inputX" )

    # Creation of reverse node + switch ik fk connection

    for i in range (len(fkCtrls)):

        mc.addAttr( fkCtrls[i].C, ln = switchAt, at = "long", minValue = 0, maxValue = 1, k = 1)
        mc.connectAttr( cogCtrl.C + "." + switchAt , fkCtrls[i].C + ".v")
        mc.connectAttr(cogCtrl.C + "." + switchAt, fkCtrls[i].C + "." + switchAt)

    for j in range ( len(ikCtrls)):

        mc.addAttr(ikCtrls[j].C, ln=switchAt, at="long", minValue=0, maxValue=1, k=1)
        mc.connectAttr( reverse_node + ".outputX", ikCtrls[j].C + ".v")
        mc.connectAttr( reverse_node + ".outputX", ikCtrls[j].C + "." + switchAt)

    #Blending parent constraint

    blending_reverse_node = mc.shadingNode("reverse", asUtility=True, name = reverseNodePrefix)

    mc.connectAttr(cogCtrl.C + "." + switchAt, blending_reverse_node + ".inputX")
    # can use either len of fkChain or ikChain same number but different objects
    for i in range(len(fkChain)):
        mc.connectAttr(cogCtrl.C + "." + switchAt, listOfParentConstraints[i] + ".w0")

        mc.connectAttr(blending_reverse_node + ".outputX", listOfParentConstraints[i] + ".w1")

    # Parent Matrix Offset Transfer &  #Joint Orient reset

    for i in range ( len(ikChain)):
        ParentOffsetMatrixTransfer.parentOffsetTransfer(ikChain[i])
        for axis in ["X","Y",'Z']:
            mc.setAttr(ikChain[i] + ".jointOrient" + axis, 0)
    for i in range ( len(fkChain)):
        ParentOffsetMatrixTransfer.parentOffsetTransfer(fkChain[i])
        for axis in ["X","Y",'Z']:
            mc.setAttr(fkChain[i] + ".jointOrient" + axis, 0)


    #FK Spine : Parent offset Matrix linking

    for i in range ( len(fkCtrls)):
        if i == 0 :
            mc.connectAttr( fkCtrls[i].C + ".worldMatrix[0]", fkChain[i] + ".offsetParentMatrix")
        else:
            mc.connectAttr(fkCtrls[i].C + ".translate", fkChain[i] + ".translate")
            mc.connectAttr(fkCtrls[i].C + ".rotate", fkChain[i] + ".rotate")


    #IK Spine : Creating Joints

    for i in range(3):
        mc.connectAttr( ikCtrls[i+1].C + ".worldMatrix[0]",twistJoints[i] + ".offsetParentMatrix")


    # This code or the function in transform can be used but can"t be applied on controls since their translations have been
    # transfered to the offset parent matrix

    #IK Spine : Creating a IK_Spline_Handle

    spineCurveCVs = mc.ls( spineCurve + ".cv[*]", fl = 1)
    ##numSpineCVs = len(spineCurveCVs)

    ##spineCurveClusters = []

    ##for i in range ( numSpineCVs):

    ##    cls = mc.cluster( spineCurveCVs[i] , n = prefix + "cluster_%d" % ( i + 1 ))[1]
    ##    spineCurveClusters.append(cls)

    ## mc.hide(spineCurveClusters)

    spineIK = mc.ikHandle( n = prefix + "_ikh", sol = "ikSplineSolver", sj = ikChain[0], ee = ikChain[-1],
                           c = spineCurve, ccv = 0, parentCurve = 0)[0]
    mc.parent(spineIK, rigmodule.partsNoTransGrp)


    spineSkinCluster = mc.skinCluster(twistJoints[0], twistJoints[1], twistJoints[2], spineCurve, tsb = True )[0]



    mc.skinPercent( spineSkinCluster, spineCurveCVs[0], transform = twistJoints[0])
    mc.skinPercent( spineSkinCluster, spineCurveCVs[2], transform = twistJoints[1])
    mc.skinPercent( spineSkinCluster, spineCurveCVs[4], transform = twistJoints[2])


    ## Adding Spine twist / roll functionality
    spineMultiplyDivideNode = mc.shadingNode("multiplyDivide", name = "spine_MD", asUtility = True)
    mc.setAttr(spineMultiplyDivideNode + ".operation", 1)
    mc.setAttr(spineMultiplyDivideNode + ".input2X", -1)

    hipsPlusMinusNode = mc.shadingNode("plusMinusAverage", name="hips_PMA", asUtility = True)

    twistOffsetNode = mc.shadingNode("plusMinusAverage", name = "spine_twistOffset_PMA", asUtility = True)

    mc.connectAttr(hipsCtrl.C + ".rotateY", hipsPlusMinusNode + ".input1D[0]")
    mc.connectAttr(lowerSpineCtrl.C + ".rotateY", hipsPlusMinusNode + ".input1D[1]")
    mc.connectAttr(hipsPlusMinusNode + ".output1D", spineIK + ".roll")

    mc.connectAttr(hipsCtrl.C + ".rotateY", spineMultiplyDivideNode + ".input1X")
    mc.connectAttr(spineMultiplyDivideNode + ".outputX", twistOffsetNode + ".input1D[0]")
    mc.connectAttr(shoulderCtrl.C + ".rotateY", twistOffsetNode + ".input1D[1]")
    mc.connectAttr(chestCtrl.C + ".rotateY", twistOffsetNode + ".input1D[2]")
    mc.connectAttr(twistOffsetNode + ".output1D", spineIK + ".twist")


    #Preparing Space Swapping for Arm follow
    shoulder_l_ik_grp = mc.group(n = "shoulder_l_ik_wspace", em = 1, p = shoulderCtrl.C)
    shoulder_l_fk_grp = mc.group(n= "shoulder_l_fk_wspace", em=1, p = fkCtrls[-1].C)
    shoulder_r_ik_grp = mc.group(n= "shoulder_r_ik_wspace", em=1, p = shoulderCtrl.C)
    shoulder_r_fk_grp = mc.group(n= "shoulder_r_fk_wspace", em=1, p = fkCtrls[-1].C)
    print(shoulder_l_fk_grp)
    print(shoulder_l_ik_grp)
    print(shoulder_r_ik_grp)
    print(shoulder_r_fk_grp)



    #Adding root control support




    return { "module" : rigmodule }