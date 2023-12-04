import maya.cmds as mc

import Utils.algorithms
from RigLibrary.base import module
from RigLibrary.base import control

from RigLibrary.rigs import spine

from Utils import ParentOffsetMatrixTransfer

orientAt = "orientNeck"

global neckCtrl
# THE NECK SHOULD ALSO TAKE INTO CONSIDERATION MODELS WITHOUT SHOULDERS, TO IMPLEMENT LATER ON !
def build(neckJoint, rootJoint, prefix = "neck", baseRig = None, scale =1.0, spineModule = None):

        #Creation of Neck Control / Neck Offset Grp

        rigmodule = module.Module(prefix = prefix, baseObj= baseRig)

        neckOffsetGrp = mc.group(n=prefix + "Offset_Grp", em=1, p= rigmodule.controlsGrp )

        joint_translation = mc.xform( neckJoint, query = True, translation = True, worldSpace = True)
        joint_rotation = mc.xform( neckJoint, query = True, rotation = True, worldSpace = True)

        mc.xform( neckOffsetGrp, translation = joint_translation, rotation = joint_rotation, worldSpace = True)

        global neckCtrl
        neckCtrl = control.Control(prefix= prefix, scale= scale * 10, translateTo= neckJoint,
                               rotateTo= neckJoint, shape= "circleY", lockChanels= ["s"], allowParentOffsetTransfer= False )

        mc.delete( mc.pointConstraint( neckCtrl.C, neckOffsetGrp))
        mc.delete(mc.orientConstraint(neckCtrl.C, neckOffsetGrp))

        mc.parent(neckCtrl.C, neckOffsetGrp)

        #Creation of Parent Constraints

        parentConstraint = mc.parentConstraint(spineModule.ikCtrls[-1].C, spineModule.fkCtrls[-1].C, neckOffsetGrp, wal=True, mo = True)[0]

        #Bringing IKFKSwitch

        reverse_node_name = spine.reverseNodePrefix
        reverse_node = mc.ls(type = "reverse")

        if reverse_node and reverse_node[0] == reverse_node_name:
                mc.connectAttr(spine.cogCtrl.C + "." + spine.switchAt, parentConstraint +".w1")
                mc.connectAttr(reverse_node[0] + ".outputX", parentConstraint+".w0" )


        #Linking neck_ctrl to ik and fk joints

        orientNeck = mc.addAttr(  neckCtrl.C ,ln = orientAt, at = 'long', minValue = 0, maxValue = 1, k = 1)

        mc.connectAttr(neckCtrl.C + ".translate", spine.ikChain[-1] + ".translate")
        mc.connectAttr(neckCtrl.C + ".rotate", spine.ikChain[-1] + ".rotate")

        mc.connectAttr(neckCtrl.C + ".translate", spine.fkChain[-1] + ".translate")
        mc.connectAttr(neckCtrl.C + ".rotate", spine.fkChain[-1] + ".rotate")


