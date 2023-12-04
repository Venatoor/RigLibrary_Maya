import maya.cmds as mc

import Utils.algorithms
from RigLibrary.base import module
from RigLibrary.base import control

from Utils import ParentOffsetMatrixTransfer


def build(chainJoints,
          chainCurve,
          prefix="ikChain",
          scale=1.0,
          fkParenting=True,
          baseRig=None):
    rigmodule = module.Module(prefix=prefix, baseObj=baseRig)

    chainCurveCVs = mc.ls(chainCurve + ".cv[*]", fl=1)
    numChainCVs = len(chainCurveCVs)

    chainCurveClusters = []

    for i in range(numChainCVs):
        chainCluster = mc.cluster(chainCurveCVs[i], n=prefix + "Cluster%d" % (i + 1))[1]
        ParentOffsetMatrixTransfer.parentOffsetTransfer(chainCluster)
        chainCurveClusters.append(chainCluster)

    mc.hide(chainCurveClusters)

    mc.parent(chainCurve, rigmodule.partsNoTransGrp)

    chainControls = []

    for i in range(numChainCVs):
        ctrl = control.Control(prefix=prefix + "%d" % (i + 1), scale=scale * 8, translateTo=chainCurveClusters[i],
                               rotateTo=chainCurveClusters[i], parentTo=rigmodule.controlsGrp, shape="circleZ")

        chainControls.append(ctrl)

    if fkParenting:
        for i in range(numChainCVs):
            if i == 0:
                continue

            mc.parent(chainControls[i].C, chainControls[i - 1].C)

    # attaching clusters + first control

    """
        for i in range ( numChainCVs ) :
            if i == 0:
                mc.connectAttr(chainControls[i].C + ".worldMatrix[0]", chainCurveClusters[i] + ".offsetParentMatrix")
            else:
                mc.connectAttr(chainControls[i].C + ".translate", chainCurveClusters[i] + ".translate")
                mc.connectAttr(chainControls[i].C + ".rotate", chainCurveClusters[i] + ".rotate")
        """

    # attaching clusters

    for i in range(len(chainCurveClusters)):
        mc.parent(chainCurveClusters[i], chainControls[i].C)

    # make ik Handle

    chainIK = mc.ikHandle(n=prefix + "_ikh", sol="ikSplineSolver", sj=chainJoints[0], ee=chainJoints[-1],
                          c=chainCurve, ccv=0, parentCurve=0)[0]

    mc.hide(chainIK)
    mc.parent(chainIK, rigmodule.partsNoTransGrp)

    twistAt = "twist"
    mc.addAttr(chainControls[-1].C, ln=twistAt, k=1)
    mc.connectAttr(chainControls[-1].C + "." + twistAt, chainIK + '.twist')

    # this module needs fk/ik configuration

    return {"module": module}
