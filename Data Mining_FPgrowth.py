#Data Mining-FPgrowth
#author:ygh


#FP树中节点的类定义
class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None #nodeLink 变量用于链接相似的元素项
        self.parent = parentNode #指向当前节点的父节点
        self.children = {} #空字典，存放节点的子节点

    def inc(self, numOccur):
        self.count += numOccur

    #将树以文本形式显示
    def disp(self, ind=1):
        print ('  ' * ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.disp(ind + 1)


#构建FP-tree
def createTree(dataSet, minSup=1):
    #创建字典headerTable
    headerTable = {}
    #第一次遍历：统计各个数据的频繁度
    for trans in dataSet:
        for item in trans:
            #用头指针表统计各个类别的出现的次数，计算频繁量：头指针表[类别]=出现次数
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]
            
    #删除未达到最小频繁度的数据
    for  k in list(headerTable):
        if headerTable[k] < minSup:
            del (headerTable[k])
    #print(headerTable)
    #保存达到要求的数据
    freqItemSet = set(headerTable.keys()) 
    #print ('freqItemSet: ',freqItemSet)

    if len(freqItemSet) == 0:
        #若达到要求的数目为0
        return None, None
    #否则遍历头指针表
    for k in headerTable:
        #保存计数值及指向每种类型第一个元素项的指针
        headerTable[k] = [headerTable[k], None]
    #print (headerTable)

    #初始化tree
    retTree = treeNode('Null Set', 1, None)
    # 第二次遍历：
    for tranSet, count in dataSet.items():
        #print(tranSet,count)
        localD = {}
        for item in tranSet:
            #只对频繁项集进行排序
            if item in freqItemSet:
                localD[item] = headerTable[item][0]
        #print(localD)
                
        #使用排序后的频率项集对树进行填充
        if len(localD) > 0:
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)]
            #print(orderedItems)
            #populate tree with ordered freq itemset
            updateTree(orderedItems, retTree, headerTable, count)
    #返回树和头指针表
    return retTree, headerTable


def updateTree(items, inTree, headerTable, count):
    # 首先检查是否存在该节点
    if items[0] in inTree.children:
        # 存在则计数增加
        inTree.children[items[0]].inc(count)
    else:
        #创建一个新节点
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        # 若原来不存在该类别，更新头指针列表
        if headerTable[items[0]][1] == None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    #仍有未分配完的树，迭代
    if len(items) > 1:
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)


#节点链接指向树中该元素项的每一个实例。
# 从头指针表的 nodeLink 开始,一直沿着nodeLink直到到达链表末尾
def updateHeader(nodeToTest, targetNode):
    while (nodeToTest.nodeLink != None):
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode


      
#createInitSet() 用于实现上述从列表到字典的类型转换过程
def createInitSet(dataSet):
    retDict = {}
    for trans in dataSet:
        retDict[frozenset(trans)] = 1
    return retDict


#从FP树中发现频繁项集
def ascendTree(leafNode, prefixPath):
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)


def findPrefixPath(basePat, treeNode):
    condPats = {}
    while treeNode != None:
        prefixPath = []
        #寻找当前非空节点的前缀
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            #将条件模式基添加到字典中
            condPats[frozenset(prefixPath[1:])] = treeNode.count 
        treeNode = treeNode.nodeLink
    return condPats

#递归查找频繁项集
def mineTree(inTree, headerTable, minSup, preFix, freqItemList):
    # 头指针表中的元素项按照频繁度排序,从小到大
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: str(p[1]))]
    
    #从底层开始
    for basePat in bigL:
        #加入频繁项列表
        newFreqSet = preFix.copy()
        newFreqSet.add(basePat)
        
        print ('\n','finalFrequent Item:',newFreqSet)
        freqItemList.append(newFreqSet)
        
        
        #递归调用函数来创建基
        condPattBases = findPrefixPath(basePat, headerTable[basePat][1])

        print ('condPattBases :',basePat, condPattBases)

        
        #构建条件模式Tree
        myCondTree, myHead = createTree(condPattBases, minSup)
        #将创建的条件基作为新的数据集添加到fp-tree
        print ('head from conditional tree: ', myHead)

        """
        support_data[frozenset(newFreqSet)]=count1
        """
        
        print ('conditional tree for: ',newFreqSet)
        
        #if Tree!=None,递归
        if myHead != None: 
            myCondTree.disp(1)
            mineTree(myCondTree, myHead, minSup, newFreqSet, freqItemList)
        

def fpGrowth(dataSet, minSup=3):
    initSet = createInitSet(dataSet)
    myFPtree, myHeaderTab = createTree(initSet, minSup)
    freqItems = []
    support_data={}
    mineTree(myFPtree, myHeaderTab, minSup, set([]), freqItems)
    support_data=create_support_data(support_data,freqItems)
    return freqItems,support_data

def create_support_data(support_data,freqItems):
    initSet_support = createInitSet(dataSet)
    for freq_set in freqItems:
        support_data[frozenset(freq_set)]=0
        for initSet_dataSet in initSet_support:
            
            if (frozenset(freq_set)).issubset(initSet_dataSet):
                support_data[frozenset(freq_set)]+=1

    return support_data
    


if __name__=="__main__":
    
    dataSet = [['M', 'O', 'N','K','E','Y'], ['D', 'O','N','K','E','Y'], ['M', 'A','K','E'],
                ['M', 'U', 'C','K','Y'], ['C', 'O','O', 'K','I','E']]

    freqItems,support_data=fpGrowth(dataSet,3)
    
    print(support_data)
