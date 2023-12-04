import maya.cmds as mc

import Utils.algorithms
from RigLibrary.base import module
from RigLibrary.base import control

from Utils import ParentOffsetMatrixTransfer


def build(spineJoints,
          rootJoint,
          spineCurve,
          prefix = 'spine',
          rigScale = 1.0,
          baseRig = None
          ):

    #making rig module


    twistJoints= []

    ikCtrls = []

    rigmodule = module.Module(prefix = prefix, baseObj = baseRig)

    #Creating the twist joints

    lengthSpineJoints = len(spineJoints)
    for i in range(0, lengthSpineJoints):
        prefix = Utils.algorithms.RemoveSuffix(spineJoints[i])
        prefix = prefix[:]





    lowerSpineCtrl = control.Control(prefix=prefix + "ik_lowerSpine", scale=rigScale * 24,
                                     translateTo=spineJoints[0], rotateTo=spineJoints[0],
                                     shape="circleX", parentTo=rigmodule.controlsGrp, lockChanels=["s"])
    twistJoints.append(mc.duplicate(spineJoints[0], n="ik_lowerSpine" + "_Twist1_Jnt", parentOnly=True)[0])

    chestCtrl = control.Control(prefix=prefix + "ik_chest", scale=rigScale * 24,
                                translateTo=spineJoints[2], rotateTo=spineJoints[2],
                                shape="circleX", parentTo=lowerSpineCtrl.C, lockChanels=["s"])
    twistJoints.append(mc.duplicate(spineJoints[2], n="ik_chest" + "_Twist1_Jnt", parentOnly=True)[0])

    shoulderCtrl = control.Control(prefix=prefix + "ik_shoulder", scale=rigScale * 24,
                                   translateTo=spineJoints[-1], rotateTo=spineJoints[-1],
                                   shape="circleX", parentTo=chestCtrl.C, lockChanels=["s"])
    twistJoints.append(mc.duplicate(spineJoints[-1], n="ik_shoulder" + "_Twist1_Jnt", parentOnly=True)[0])

    for i in range(len(twistJoints)):
        mc.setAttr(twistJoints[i] + ".radius", 10)
        mc.parent(twistJoints[i], rigmodule.jointsGrp)
        ParentOffsetMatrixTransfer.parentOffsetTransfer(twistJoints[i])

    ikCtrls.append(lowerSpineCtrl)
    ikCtrls.append(chestCtrl)
    ikCtrls.append(shoulderCtrl)


    # Parent Matrix Offset Transfer &  #Joint Orient reset

    ParentOffsetMatrixTransfer.parentOffsetTransfer(rootJoint)
    for axis in ["X", "Y", 'Z']:
        mc.setAttr(rootJoint + ".jointOrient" + axis, 0)


    for i in range ( lengthSpineJoints):
        ParentOffsetMatrixTransfer.parentOffsetTransfer(spineJoints[i])
        for axis in ["X","Y",'Z']:
            mc.setAttr(spineJoints[i] + ".jointOrient" + axis, 0)

    for i in range ( len(twistJoints)):
        ParentOffsetMatrixTransfer.parentOffsetTransfer(twistJoints[i])
        for axis in ["X","Y",'Z']:
            mc.setAttr(twistJoints[i] + ".jointOrient" + axis, 0)




    # IK Spine : Creating Joints

    for i in range(3):
        mc.connectAttr( ikCtrls[i].C + ".worldMatrix[0]",twistJoints[i] + ".offsetParentMatrix")

    # IK Spine : Creating a IK_Spline_Handle



    spineCurveCVs = mc.ls( spineCurve + ".cv[*]", fl = 1)
    ##numSpineCVs = len(spineCurveCVs)

    ##spineCurveClusters = []

    ##for i in range ( numSpineCVs):

    ##    cls = mc.cluster( spineCurveCVs[i] , n = prefix + "cluster_%d" % ( i + 1 ))[1]
    ##    spineCurveClusters.append(cls)

    ## mc.hide(spineCurveClusters)


    spineIK = mc.ikHandle( n = prefix + "_ikh", sol = "ikSplineSolver", sj = rootJoint, ee = spineJoints[-1],
                           c = spineCurve, ccv = 0, parentCurve = 0)[0]
    mc.parent(spineIK, rigmodule.partsNoTransGrp)


    spineSkinCluster = mc.skinCluster(twistJoints[0], twistJoints[1], twistJoints[2], spineCurve, tsb = True )[0]



    mc.skinPercent( spineSkinCluster, spineCurveCVs[0], transform = twistJoints[0])
    mc.skinPercent( spineSkinCluster, spineCurveCVs[2], transform = twistJoints[1])
    mc.skinPercent( spineSkinCluster, spineCurveCVs[-1], transform = twistJoints[2])



    return { "module" : rigmodule }