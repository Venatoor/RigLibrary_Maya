import maya.cmds as mc

import Utils.transform
from Utils import transform
from Utils import ParentOffsetMatrixTransfer

class Control():

    def __init__(self,
                 prefix = "",
                 scale = 1.0,
                 translateTo = "",
                 rotateTo = "",
                 shape = "",
                 parentTo = "",
                 lockChanels=None,
                 allowParentOffsetTransfer = True):

        if lockChanels is None:
            lockChanels = ["s", "v"]

        """
        :param prefix :  str, prefix to name new controls
        :param scale : float, scale of the control
        :param translateTo : str, name of the object to translate the control to 
        :param rotateTo : str, name of the object to rotate the control to
        :param shape : str, name of the shape that the control should take
        :param parentTo: str, name of the object to parent the control to 
        :param lockChanels: char[], characters of the attributes to lock in the translation field 
        
        :return:  Void
        
        """


        #PROCESSING SHAPE PARAMETER

        ctrlObject = None
        circleNormal = [1,0,0]

        if shape in ["circleX", "circle"]:

            circleNormal = [1,0,0]

        elif shape == "circleY":

            circleNormal = [0,1,0]

        elif shape == "circleZ":

            circleNormal = [0,0,1]


        ctrlObject = mc.circle( n = prefix + "_ctrl", normal = circleNormal, ch = False, radius = scale)[0]


        #FIXING COLOR FOR LEFT/RIGHT SIDE

        mc.setAttr( ctrlObject + ".ove", 1)

        if ( prefix.startswith("l_")):

            mc.setAttr( ctrlObject + ".ovc", 13)

        elif ( prefix.startswith("r_")):

            mc.setAttr( ctrlObject + ".ovc", 22)

        else:
            mc.setAttr( ctrlObject + ".ovc", 6 )


        #FREEZING THE CONTROL

        transform.freezeTransform( ctrlObject, translate= False, scale = True, rotation= False, jointOrient= False)


        #DELETING HISTORY OF CONTROL

        mc.delete( ctrlObject, ch = True)

        #TRANSLATING THE CONTROL

        if ( translateTo ) :

            mc.delete( mc.pointConstraint( translateTo, ctrlObject))

        #ROTATING THE CONTROL

        if ( rotateTo ) :

            mc.delete( mc.orientConstraint( rotateTo, ctrlObject))

        #PARENTING THE CONTROL

        if ( parentTo) :

            mc.parent(ctrlObject, parentTo)

        #PARENT OFFSET MATRIX TRANSFER

        if ( allowParentOffsetTransfer ):
            ParentOffsetMatrixTransfer.parentOffsetTransfer( ctrlObject )


        #LOCKING ATTRIBUTES

        singleAttributeLockList = []
        for lockChanel in lockChanels:
            if lockChanel in ['t','r','s']:
                for axis in ["x",'y','z']:
                    at = lockChanel + axis
                    singleAttributeLockList.append(at)
            else:
                singleAttributeLockList.append(lockChanel)
        for at in singleAttributeLockList:
           mc.setAttr( ctrlObject + "." + at, l = 1, k = 0 )

        self.C = ctrlObject


