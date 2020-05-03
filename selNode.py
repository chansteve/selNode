import maya.cmds as cmds
import re

# identify selection node.
def selectionNodeIdentify(node):
    selNode = re.compile('^selNode')
    udAttr  = cmds.listAttr(node, ud=1)
    if udAttr:
        if any(selNode.search(n) for n in udAttr):
            return True
    else:
        return False
    
    
# create node and attribute for storage selection.
def create(members, kName="userDefine"):
    #print 'test version'
    if members:
        num = 1
        nodeName = kName+"_selNode"
        while cmds.ls(nodeName):
            nodeName = kName+str(num)+"_selNode"
            num+=1

        node  = cmds.group(em=1, w=1, n=nodeName)
        attrs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]
        for attr in attrs:
            cmds.setAttr(node+"."+attr, l=1)
            cmds.setAttr(node+"."+attr, k=0)
        
        print "# Created node '%s'." %node
        attrDic = {}
        for member in members:
            #handle name clash problem
            memberList = []
            if '|' in member:
                dagName = member.split('|')
                for dag in dagName:
                    memberList.append(dag.split(':')[-1])
                memberList = '|'.join(memberList)
            if ':' in member:
                attrsName   = "selNode_"+member.split(":")[0]
                attrDic.setdefault(attrsName,[])
                #have name clash problem change member value
                if len(memberList):
                    attrDic[attrsName].append(memberList)
                else:
                    attrDic[attrsName].append(member.split(":")[1])
            else:
                attrsName   = "selNode_default"
                attrDic.setdefault(attrsName,[])
                if len(memberList):
                    attrDic[attrsName].append(memberList)
                else:
                    attrDic[attrsName].append(member)
        for attr,value in attrDic.items():
            if not cmds.attributeQuery(attr, n=node, ex=1):
                cmds.addAttr(node, dt="string", ln=attr)
            attrValue = ','.join(value)
            cmds.setAttr(node+"."+attr, attrValue, typ="string")    
            
    else:
        return None
    
    return node


# read selection node objects.
def read(nodes):
    members = []
    for node in nodes:
        # if locked node define node is referenced.
        if ":" in node:
            namespace = node.split(":")[0]+":"
            udAttrs   = cmds.listAttr(node, ud=1)
            if udAttrs:
                for attr in udAttrs:
                    if len(cmds.getAttr(node+"."+attr)) == 0 or "orgPos0" == attr:
                        continue
                    for val in cmds.getAttr(node+"."+attr).split(","):
                        if "|" in val:
                            partSplit = val.split("|")
                            reVal     = namespace+partSplit[0]
                            for part in partSplit[1:]:
                                reVal = reVal+"|"+namespace+part
                            members.append(reVal)
                        else:
                            members.append(namespace+val)
        # else define node is local.
        else:
            udAttrs = cmds.listAttr(node, ud=1)
            if udAttrs:
                for attr in udAttrs:
                    #20190523 refine attr checking.
                    #if len(cmds.getAttr(node+"."+attr)) == 0 or "orgPos0" == attr:
                    if attr.startswith("selNode_"):
                        if attr == "selNode_default":
                            namespace = ""
                        else:
                            namespace = attr.replace("selNode_", "")+":"
                    else:
                        continue
                    for val in cmds.getAttr(node+"."+attr).split(","):
                        if "|" in val:
                            partSplit = val.split("|")
                            reVal     = namespace+partSplit[0]
                            for part in partSplit[1:]:
                                reVal = reVal+"|"+namespace+part
                            members.append(reVal)
                        else:
                            members.append(namespace+val)
    returnMembers = []
    for member in members:
        if cmds.ls(member):
            returnMembers.append(member)
        else:
            print "# '%s' not found."%member
        
        
    return returnMembers
    

# add selection node attribute.
def add(newMembers, node):
    if cmds.listRelatives(node, ad=1, pa=1):
        nodes = [node] + cmds.listRelatives(node, ad=1, pa=1)
    else:
        nodes = [node]
        
    newNodeMember = []
    for member in newMembers:
        if ":" in member:
            memberNamespace = member.split(":")[0]
        else:
            memberNamespace = ""
        
        for node in nodes:
            if ":" in node:
                nodeNamespace = node.split(":")[0]
            else:
                nodeNamespace = ""

            if len(nodeNamespace) == 0 and len(memberNamespace) > 0:
                attrsName, addVal = "selNode_"+member.split(":")[0], member.split(":")[1]
            elif len(nodeNamespace) == 0 and len(memberNamespace) == 0:
                attrsName, addVal = "selNode_default", member
            elif len(nodeNamespace) > 0 and len(memberNamespace) == 0:
                if node == nodes[-1]:
                    newNodeMember.append(member)
                    break
                continue
            elif len(nodeNamespace) > 0 and len(memberNamespace) > 0:
                if nodeNamespace == memberNamespace:
                    attrsName, addVal = "selNode_default", member.split(":")[1]
                else:
                    continue
            elif node == nodes[-1]:
                newNodeMember.append(member)
                break
                
            if cmds.attributeQuery(attrsName, n=node, ex=1):
                if addVal in cmds.getAttr(node+"."+attrsName).split(","):
                    print "# '%s' already in '%s'." %(member, node)
                    break
                else:
                    if cmds.getAttr(node+"."+attrsName):
                        attrVal = cmds.getAttr(node+"."+attrsName)+","+addVal
                    else:
                        attrVal = addVal
                    cmds.setAttr(node+"."+attrsName, attrVal, typ="string")
                    print "# '%s' added in '%s'." %(member, node)
                    break
            else:
                attrVal = addVal
                cmds.addAttr(node, dt="string", ln=attrsName)
                print "# Created attribute '%s.%s'." %(node, attrsName)
                cmds.setAttr(node+"."+attrsName, attrVal, typ="string")
                print "# '%s' added in '%s'." %(member, node)
                break

    if newNodeMember:
        newNode = create(newNodeMember)
        cmds.parent(newNode, node)
        
        for newMember in newNodeMember:
            print "# Added '%s' to %s."%(newMember, newNode)

        
        return node + newNode
    
    
    return node


# remove selection node attribute.
def remove(rmMembers, node):
    if cmds.listRelatives(node, ad=1, pa=1):
        nodes = [node] + cmds.listRelatives(node, ad=1, pa=1)
    else:
        nodes = [node]
        
    for member in rmMembers:
        if ":" in member:
            memberNamespace = member.split(":")[0]
        else:
            memberNamespace = ""

        for node in nodes:
            if ":" in node:
                nodeNamespace = node.split(":")[0]
            else:
                nodeNamespace = ""

            if len(nodeNamespace) == 0 and len(memberNamespace) > 0:
                attrsName, rmVal = "selNode_"+member.split(":")[0], member.split(":")[1]
            elif len(nodeNamespace) == 0 and len(memberNamespace) == 0:
                attrsName, rmVal = "selNode_default", member
            elif len(nodeNamespace) > 0 and len(memberNamespace) == 0:
                continue
            elif len(nodeNamespace) > 0 and len(memberNamespace) > 0:
                if nodeNamespace == memberNamespace:
                    attrsName, rmVal = "selNode_default", member.split(":")[1]
                else:
                    continue
            elif node == nodes[-1]:
                print "# '%s' not in selection node(s)." %member
                
            if cmds.attributeQuery(attrsName, n=node, ex=1):
                oldVal = cmds.getAttr(node+"."+attrsName).split(",")
                if rmVal in oldVal:
                    oldVal.remove(rmVal)
                    if len(oldVal) > 1:
                        attrVal = oldVal[0]
                        for val in oldVal[1:]:
                            attrVal = attrVal+","+val
                    elif len(oldVal) == 1:
                        attrVal = oldVal[0]
                    else:
                        attrVal = ""
                    cmds.setAttr(node+"."+attrsName, attrVal, typ="string")
                    print "# Removed '%s' from '%s'." %(member, node)
                else:
                    if node == nodes[-1]:
                        print "# '%s' not in selection node(s)." %member
                    continue
            else:
                continue
    
    return node


def prueRead(nodes):
    members = []
    for node in nodes:
        udAttrs = cmds.listAttr(node, ud=1)
        if udAttrs:
            for attr in udAttrs:
                if "orgPos0" in attr:
                    continue
                else:
                    for val in cmds.getAttr(node+"."+attr).split(","):
                        members.append(val)
    
    returnMembers = []
    for member in members:
        if cmds.ls(member):
            returnMembers.append(member)
        else:
            print "# '%s' not found."%member
        
        
    return returnMembers

