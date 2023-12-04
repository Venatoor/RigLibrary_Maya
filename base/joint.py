import maya.cmds as mc

def listHierarchy( topJoint):

    listedJoints = mc.listRelatives(topJoint, type = "joint", ad = True)
    listedJoints.append(topJoint)
    listedJoints.reverse()

    completeJoints = listedJoints[:]

    return completeJoints