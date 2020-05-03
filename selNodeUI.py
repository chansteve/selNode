import selNode as selNode
import maya.cmds  as cmds
import pymel.core as pm

# class ui.
class Ui():

    uiAnn = {
        'kwTxt'         : 'Enter the keywords to filter the selection.',
        'createNode'    : 'Select object(s) press button to select selection Node.',
        'selNode'       : 'Select Node Node press button to select objects.',
        'addToNode'     : 'Select object(s) press button add to selection Node',
        'reMoveFrmNode' : 'Select object(s) press button remove from selection Node',
        }

    def __init__(self):
        windowID = 'selNodeWnd'

        if pm.window('selNodeWnd', exists=1):
            pm.deleteUI('selNodeWnd')

        tmpl = pm.uiTemplate(windowID+'_uiTmpl', force=1)
        tmpl.define('columnLayout', adj=1, cat=('both', 5), rs=5)
        tmpl.define('button', h=40)
        tmpl.define('textFieldGrp', cl2=['center', 'left'], ad2=2, cw2=[30, 40])
        tmpl.define('checkBoxGrp', v1=0, cw=[1,80])
        
        wnd = pm.window(windowID, t='Sel Node Editor', s=1, rtf=1, toolbox=1)

        with tmpl:
            with pm.columnLayout():
                with pm.horizontalLayout() as createLayout:
                    pm.textFieldGrp('nameTxt', l='Node Name', ann=self.uiAnn['kwTxt'], cw2=[80, 80], cal=[1, 'left'], en=1,  tx="userNode",)
                    pm.button('createNodeBtn', l='Create Node', ann=self.uiAnn['createNode'], w=30, c=self.createNodeBtnCmd)
                with pm.horizontalLayout() as kwTxtLayout:
                    pm.textFieldGrp('kwTxt', l='Searching KeyWords', ann=self.uiAnn['kwTxt'], cw2=[110, 40], cal=[1, 'left'], en=1)
                with pm.horizontalLayout() as btnLayout3:
                    pm.button('readNodeBtn'     , l='Read Node'      , ann=self.uiAnn['selNode']      , c=self.readNodeBtnCmd)
                    pm.button('addToNodeBtn'    , l='Add to Node'    , ann=self.uiAnn['addToNode']    , c=self.addToNodeBtnCmd)
                    pm.button('reMoveFrmNodeBtn', l='Remove Frm Node', ann=self.uiAnn['reMoveFrmNode'], c=self.reMoveFrmNodeCmd)
                    
        wnd.show()
    
    def createNodeBtnCmd(self, *arg):
        name = pm.textFieldGrp('nameTxt', q=1, tx=1)
        selNode.create(cmds.ls(sl=1, sn=1), name)
    
    def readNodeBtnCmd(self, *arg):
        kwTxtVal = pm.textFieldGrp('kwTxt', q=1, tx=1).replace(' ', '').split(',')
        if kwTxtVal:
            if cmds.listRelatives(cmds.ls(sl=1), ad=1, pa=1):
                readObjs = cmds.ls(selNode.read(cmds.ls(sl=1) + cmds.listRelatives(cmds.ls(sl=1), ad=1, pa=1)))
            else:
                readObjs = cmds.ls(selNode.read(cmds.ls(sl=1)))
            objs     = []
            for obj in readObjs:
                num = len(kwTxtVal)
                for txt in range(0, num):
                    if kwTxtVal[txt] in obj:
                        objs.append(obj)
            cmds.select(objs)
        else:
            print cmds.listRelatives(cmds.ls(sl=1), ad=1, pa=1)
            if cmds.listRelatives(cmds.ls(sl=1), ad=1, pa=1):
                readObjs = cmds.ls(selNode.read(cmds.ls(sl=1) + cmds.listRelatives(cmds.ls(sl=1), ad=1, pa=1)))
            else:
                readObjs = cmds.ls(selNode.read(cmds.ls(sl=1)))
            cmds.select(readObjs)
        print "#-----------------#"
        for obj in readObjs:
            print "# %s" %obj
        print "# Object(s) selected."
        
    def addToNodeBtnCmd(self, *arg):
        selNode.add(cmds.ls(sl=1, sn=1)[:-1], cmds.ls(sl=1)[-1])
    
    def reMoveFrmNodeCmd(self, *arg):
        selNode.remove(cmds.ls(sl=1, sn=1)[:-1], cmds.ls(sl=1)[-1])

Ui()
