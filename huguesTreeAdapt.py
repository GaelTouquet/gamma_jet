from ROOT import TFile
import numpy

def findHLTPt(pt):
    """gets the pt of the associated HLT for each ptbin (here pt is ptmin of the bin)"""
    if pt >=175. :
        return 165
    if pt >=130. :
        return 120
    if pt >=105. :
        return 90
    if pt >=85. :
        return 75
    if pt >=60. :
        return 50
    if pt >=40. :
        return 30
    else:
        print "error! pt have to be greater than 40."
        return False

########################################################################
class puweighter:
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.hltptlist = [30, 50, 75, 90, 120, 165]
        self.files = {}
        self.hists = {}
        for hltpt in self.hltptlist:
            self.files[hltpt] = TFile('PUFiles/PUprofile{HLTPT}.root'.format(HLTPT=hltpt))
            self.hists[hltpt] = self.files[hltpt].Get('pileup')
        
    #----------------------------------------------------------------------
    def puweightHist(self, hltpt):
        """"""
        return self.hists[hltpt]
    
PUweighter = puweighter()

def getPUweight(HLTPT, nvertex):
    """retrieves the pu weight depending on which HLT was passed"""
    hist = PUweighter.puweightHist(HLTPT)
    return hist.GetBinContent(hist.FindBin(nvertex))

def setTree(tree, isMC):
    """adapts tree with Tot_weight variable added"""
    weight = numpy.zeros(1,numpy.float32)
    branch = tree.Branch("Tot_weight",
                         weight,
                         "Tot_weight/F")
    i = 0
    Nevent = tree.GetEntries()
    for event in tree:
        i+=1
        if i%10000==0:
            print 'treating', 'MC' if isMC else 'Data', 'event ', i, '/', Nevent
        if not isMC:
            weight[0] = 1.
            branch.Fill()
            continue
        else:
            HLTPT = findHLTPt(event.Pt_photon)
            puWeight = getPUweight(HLTPT, event.trueInteraction)
            generatorweight = event.weight
            evweighttotA = event.evtWeightTotA
            weight[0] = puWeight * generatorweight * evweighttotA
            branch.Fill()



#fil = TFile.Open('hugues.root')
#tree = fil.Get('tree')
#fil2 = TFile.Open('test.root','recreate')
#tree2 = tree.CloneTree()
#setTree(tree2, True)
#tree2.Write()
#fil2.Close()

print 'opening MC file'
filemc = TFile('huguesMCfull.root')
roottreemc = filemc.Get('rootTupleTree').Get('tree')
print 'got MC tree'
mcfile = TFile('MCfull.root','recreate')
print 'cloning tree...'
basetreemc = roottreemc.CloneTree(5000000)
print 'adding weight branch'
setTree(basetreemc, True)
basetreemc.Write()
mcfile.Close()

#print 'opening Data file'
#filedata = TFile('huguesDATAfull.root')
#roottreedata = filedata.Get('rootTupleTree').Get('tree')
#print 'got Data tree'
#datafile = TFile('DATAfull.root','recreate')
#print 'cloning tree...'
#basetreedata = roottreedata.CloneTree()
#print 'adding weight branch'
#setTree(basetreedata, True)
#basetreedata.Write()
#datafile.Close()
