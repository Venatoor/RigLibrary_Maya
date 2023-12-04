import maya.cmds as mc

import Utils.algorithms
from RigLibrary.base import module
from RigLibrary.base import control

from Utils import ParentOffsetMatrixTransfer

def build( prefix = "head", headJoint = "", neckModule= "",
           baseRig = None, worldSpaceLocator = "", scale = 1.0,
           rootJoint = ""):

    rigmodule = module.Module( prefix = prefix, baseObj= baseRig)

    #REQUIRES THE NECK MODULE

    #CREATION OF HEAD OFFSET GROUP

    headOffsetGrp = mc.group(n=prefix + "Offset_Grp", em=1, p=rigmodule.controlsGrp)

    joint_translation = mc.xform(headJoint, query=True, translation=True, worldSpace=True)
    joint_rotation = mc.xform(headJoint, query=True, rotation=True, worldSpace=True)

    mc.xform(headOffsetGrp, translation=joint_translation, rotation=joint_rotation, worldSpace=True)

    headCtrl = control.Control(prefix=prefix, scale=scale * 10, translateTo=headJoint,
                                shape="circleY", lockChanels=["s"], allowParentOffsetTransfer=False)

    mc.delete(mc.pointConstraint(headCtrl.C, headOffsetGrp))
    mc.delete(mc.orientConstraint(headCtrl.C, headOffsetGrp))

    mc.parent(headCtrl.C, headOffsetGrp)

    # TRANSLATION PARENT CONSTRAINT

    parentConstraintTranslation = mc.parentConstraint(neckModule.neckCtrl.C,  headOffsetGrp, wal=True, mo=True, name = "Head_Translation_Constraint",
                                           skipRotate = ("x","y","z"))[0]

    parentConstraintRotation = mc.parentConstraint(neckModule.neckCtrl.C, worldSpaceLocator, headOffsetGrp, wal = True, mo = True,
                                                   name = "Head_Rotation_Constraint", skipTranslate = ("x","y","z"))[0]

    jointParentConstraint = mc.parentConstraint(headCtrl.C, headJoint, name = "Head_Joint_Constraint", wal = True, mo = True)

    #CONNECTING NECK ORIENT TO PARENT CONSTRAINT ROTATION

    reverse_orientNeck = mc.shadingNode("reverse", asUtility = True, name = "Reverse_OrientNeck")

    mc.connectAttr(neckModule.neckCtrl.C + "." + neckModule.orientAt, reverse_orientNeck + ".inputX")
    mc.connectAttr(neckModule.neckCtrl.C + "." + neckModule.orientAt, parentConstraintRotation + ".w0")
    mc.connectAttr(reverse_orientNeck + ".outputX", parentConstraintRotation + ".w1")






