import maya.cmds as mc
from . import control

sceneObjectType = "rig"

class Base():

        def __init__(self, characterName = "", scale = 1.0, mainCtrlAttachObj = ""):

            """

            :param characterName: STR, name of the base rig
            :param scale: FLOAT, scale of the base rig
            :param mainCtrlAttachObj: WIP
            """

            self.topGrp = mc.group( n = characterName + "rip_grp", em = 1)
            self.modelGrp = mc.group( n = "model_grp", em = 1, p = self.topGrp)
            self.ripGrp = mc.group( n = "rip_grp", em = 1, p = self.topGrp)

            characterNameAt = "characterName"
            sceneObjectTypeAt = "sceneObjectType"

            for att in [characterNameAt, sceneObjectTypeAt]:
                mc.addAttr( self.topGrp, ln=att, dt = "string")

            mc.setAttr( self.topGrp + "." + characterNameAt, characterName, type ="string", l = 1)
            mc.setAttr( self.topGrp + "." + sceneObjectTypeAt, sceneObjectType, type = "string", l = 1)

            rootCtrl = control.Control( prefix = "root",
                                        scale = scale * 50,
                                        parentTo= self.ripGrp,
                                        lockChanels=["v"])

            self._flattenGlobalCtrlShape(rootCtrl.C)

            #making more groups

            self.jointsGroup = mc.group( n = "joints_grp", em = 1, p = rootCtrl.C)
            self.modulesGroup = mc.group( n = "modules_grp", em = 1,p = rootCtrl.C)
            self.partGroup = mc.group ( n = "parts_grp", em = 1, p = self.ripGrp)
            self.blendShapesGroup = mc.group( n = "blendShapes_grp", em = 1, p = rootCtrl.C)


            mc.setAttr( self.partGroup + ".it", 0, l = 1)


            #Adding Attributes to root ctrl

            mainVisAts = ["modelVis", "jointsVis"]
            mainDispAts = ["modelDisp", "jointsDisp"]
            mainCtrlObj = [ self.modelGrp, self.jointsGroup]
            defaultValues = [1,0]

            for at, obj, df in zip(mainVisAts, mainCtrlObj, defaultValues):

                mc.addAttr(rootCtrl.C, ln = at, at = "enum", enumName = "Hide:Show", k = 1, dv = df)
                mc.setAttr(rootCtrl.C + "." + at, cb = 1 )
                mc.connectAttr(rootCtrl.C + "." + at, obj + ".v")

            for at, obj in zip(mainDispAts, mainCtrlObj):

                mc.addAttr(rootCtrl.C, ln = at, at = "enum", enumName = "normal:template:reference", k = 1)
                mc.setAttr(rootCtrl.C + "." + at, cb =1 )
                mc.setAttr(obj + ".ove", 1 )
                mc.connectAttr(rootCtrl.C + "." + at, obj + ".ovdt")


        def _flattenGlobalCtrlShape(self, ctrlObject):
            ctrlShapes = mc.listRelatives(ctrlObject, s=1, type="nurbsCurve")
            cls = mc.cluster(ctrlShapes)[1]  ## first is name of deformer, second is the handle
            mc.setAttr(cls + '.rz', 90)
            mc.delete(ctrlShapes, ch=1)




class Module():

    def __init__(self,
                 prefix = "",
                 baseObj = None
                 ):


        """
        :param prefix : STR, name of the module
        :param baseObj : instance of base, reference to the baserig where all modules are attached
        """

        self.topGrp = mc.group( n = prefix + "Module_Grp", em = 1 )
        self.controlsGrp = mc.group( n = prefix + "Controls_Grp", em = 1, p = self.topGrp)
        self.jointsGrp = mc.group( n = prefix + "Joints_Grp", em = 1, p = self.topGrp)
        self.partsGrp = mc.group( n = prefix + "Parts_Grp", em = 1, p = self.topGrp)
        self.partsNoTransGrp = mc.group(n = prefix + "PartsNoTrans_Grp", em = 1, p = self.topGrp)

        #NEED TO ADD MORE LOGIC HERE TO STITCH MODULE TO BASE CLASS

        mc.setAttr(self.partsNoTransGrp + ".it", 0, l = 1)

        if baseObj:
            mc.parent( self.topGrp, baseObj.modulesGroup )
