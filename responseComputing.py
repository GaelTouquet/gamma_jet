from ROOT import TFile, TCanvas, TTree, TGraph
from cpyroot.tools.officialstyle import officialStyle, gStyle
from RHistsHandler import RHistsHandler
from HuguesTreeHandler import HuguesTreeHandler
import shelve

officialStyle(gStyle)

makebasetree = True # False not implemented yet
#if makebasetree:
    #filemc = TFile('huguesMCfull.root')
    #roottreemc = filemc.Get('rootTupleTree').Get('tree')
    
    #filedata = TFile('huguesDATAfull.root')
    #roottreedata = filedata.Get('rootTupleTree').Get('tree')
    
    #tempfile = TFile('tempfile.root','recreate')
    #basetreemc = roottreemc.CloneTree()
    #basetreedata = roottreedata.CloneTree()
    #tempfile.Write()
    
#else:
    #tempfile = TFile('tempfile.root')
    #basetreemc = None
    #basetreedata = None

#treemc = HuguesTreeHandler(True, basetreemc)
#treedata = HuguesTreeHandler(False, basetreedata)
filemc = TFile('MCfull.root')
treemc = filemc.Get('tree')

filedata = TFile('DATAfull.root')
filedata = filedata.Get('tree')


ptbins = [[40.0, 50.0] ,
          [50.0, 60.0] ,
          [60.0, 85.0] ,
          [85.0, 105.0] ,
          [105.0, 130.0] ,
          [130.0, 175.0] ,
          [175.0, 230.0] ,
          [230.0, 300.0] ,
          [300.0, 400.0] ,
          [400.0, 500.0] ,
          [500.0, 700.0] ,
          [700.0, 1000.0] ,
          [1000.0, 3000.0]]

etabins = [[0.,1.3],
           [1.3,2.6]]

alphas = [0.3,0.2,0.1]

nbinR = 30
xminR = 0.
xmaxR = 2.

percentIntegralmean = 0.985
percentIntegralrms = 0.985

print '##### MC'

print 'building R hists'
RHisthandlermc = RHistsHandler(ptbins, etabins, alphas, treemc, nbinR, xminR, xmaxR, 
                               verbose=True)    
print 'computing means'
RHisthandlermc.computeMeanAndRMS(percentIntegralmean, percentIntegralrms)
print 'extrapolating R0'
RHisthandlermc.extrapolateR()

print '##### Data'
print 'building R hists'

RHisthandlerdata = RHistsHandler(ptbins, etabins, alphas, treedata, nbinR, xminR, xmaxR, 
                                 verbose=True) 
print 'computing means'

RHisthandlerdata.computeMeanAndRMS(percentIntegralmean, percentIntegralrms)
print 'extrapolating R0'

RHisthandlerdata.extrapolateR()

print 'saving r0s'
shelf = shelve.open('shelvesave')
for histname in RHisthandlermc.histsnames:
    shelf[histname] = RHisthandlermc.getHist(histname)['R0']
    
for histname in RHisthandlerdata.histsnames:
    shelf[histname] = RHisthandlerdata.getHist(histname)['R0']
    
shelf.close()

varnames = ['Rbalancing','RMPF']

data_mc_file = TFile('data_mc_file.root')
graphs = {}
for varname in varnames:
    for etamin, etamax in etabins:
        pt, R0data, R0mc = [], [], []
        for ptmin, ptmax in ptbins:
            name = '_'.join([varname,
                             'eta{eta}'.format(eta=int(etamax)),
                             'pt{pt}'.format(pt=int(ptmin))
                             ])
            pt.append((ptmin+ptmax)/2.)
            R0data.append(RHisthandlerdata.getHist(histname)['R0'])
            R0mc.append(RHisthandlermc.getHist(histname)['R0'])
        datagraph = TGraph(len(pt),array('d',pt),array('d',R0data))
        datagraph.SetMarkerColor(1)
        mcgraph = TGraph(len(pt),array('d',pt),array('d',R0mc))
        mcgraph.SetMarkerColor(4)
        graphs[[varname,etamax]] = [datagraph,
                                    mcgraph])
        can = TCanvas()
        datagraph.Draw()
        mcgraph.Draw('same')
        can.SaveAs('{var}_{eta}_MC_Data.pdf'.format(var=varname,eta=etamax))