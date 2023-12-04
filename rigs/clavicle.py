import maya.cmds as mc

import Utils.algorithms
from RigLibrary.base import module
from RigLibrary.base import control

from Utils import ParentOffsetMatrixTransfer

# THE CLAVICLE REQUIRES SPINE AND ARM

def build( prefix = "clavicle", rootJoint = "", clavicleJoint = "", baseRig = None, spineModule = None, armModule = None,
           aimLocator = None, scale = 1.0):

        rigmodule = module.Module(prefix = prefix, baseObj= baseRig)

        # Translation constraint

        ikShoulderCtrl = spineModule.ikCtrls[3]
        fkSpineCtrl = spineModule.fkCtrls[3]

        translationPConstraint = mc.parentConstraint(ikShoulderCtrl.C, fkSpineCtrl.C, clavicleJoint, wal = True,
                                                     name = "Clavicle_Translation_Constraint", skipRotate = ("x","y","z"),
                                                     mo = True)[0]

        reverse_node_name = spineModule.reverseNodePrefix
        reverse_node = mc.ls(type="reverse")

        if reverse_node and reverse_node[0] == reverse_node_name:
            mc.connectAttr(spineModule.cogCtrl.C + "." + spineModule.switchAt, translationPConstraint + ".w1")
            mc.connectAttr(reverse_node[0] + ".outputX", translationPConstraint + ".w0")

        # Rotation constraint

            print(" IT ENTERS THIS SECTION !!! DEBUGGED ")
            limbControl = armModule.limbCtrl

            # I NEED MORE KNOWLEDGE ON AIM CONSTRAINT
            #aimConstraint = mc.aimConstraint( limbControl.C, clavicleJoint,mo = False, aimVector = (0,1,0), worldUpType = "object",
            #                                 worldUpObject = aimLocator, worldUpVector = (0,0,1), name = "Clavicle_Aim_Constraint" )



