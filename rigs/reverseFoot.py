import maya.cmds as mc

import Utils.algorithms
from RigLibrary.base import module
from RigLibrary.base import control

from Utils import ParentOffsetMatrixTransfer

footJoint = None

bigToeCtrls = []
indexToeCtrls = []
middleToeCtrls = []
ringToeCtrls = []
pinkyToeCtrls = []

def GetFootJoint():
    return footJoint

# THIS MODULE REQUIRES THE FOOT VERSION OF BIPEDAL LIMB TO WORK

def build(bigToeChain, indexToeChain, middleToeChain, ringToeChain, pinkyToeChain, baseRig, scale, prefix, rootJoint, legModule):

    #Checking if module is leg

    if legModule.isLeg == True:
            print(legModule.footControl.C)

    #Finding parent of first element of any serie // setting its parent as the foot

    footJoint = mc.listRelatives(bigToeChain[0], parent = True, fullPath = True)
    if footJoint:

    # Creating controls for all toe sections ( MISSING : Parenting )
        collectiveLength = len(indexToeChain)
        for i in range ( collectiveLength):

            bigToeCtrl = control.Control( bigToeChain[i], scale = scale, translateTo= bigToeChain[i], rotateTo= bigToeChain[i],
                                          shape = "circleZ", lockChanels= ["s"], allowParentOffsetTransfer= True)
            bigToeCtrls.append(bigToeCtrl)

            indexToeCtrl = control.Control( indexToeChain[i], scale = scale, translateTo= indexToeChain[i], rotateTo= indexToeChain[i],
                                          shape = "circleZ", lockChanels= ["s"], allowParentOffsetTransfer= True)

            indexToeCtrls.append(indexToeCtrl)

            middleToeCtrl = control.Control(middleToeChain[i], scale = scale, translateTo= middleToeChain[i], rotateTo= middleToeChain[i],
                                          shape = "circleZ", lockChanels= ["s"], allowParentOffsetTransfer= True)

            middleToeCtrls.append(middleToeCtrl)

            ringToeCtrl = control.Control(ringToeChain[i], scale=scale, translateTo=ringToeChain[i],
                                            rotateTo=ringToeChain[i],
                                            shape="circleZ", lockChanels=["s"], allowParentOffsetTransfer=True)

            ringToeCtrls.append(ringToeCtrl)

            pinkyToeCtrl = control.Control(pinkyToeChain[i], scale=scale, translateTo=pinkyToeChain[i],
                                            rotateTo=pinkyToeChain[i],
                                            shape="circleZ", lockChanels=["s"], allowParentOffsetTransfer=True)

            pinkyToeCtrls.append(pinkyToeCtrl)









    #FK parenting
    #reverse foot creation + parenting

    #Banks offset creation + parenting + position

    # Ik handles creation
