from HistCreator import HistCreator
from array import array
from ROOT import TH1F, TGraph, TF1

#TO DO avoid confusion between hist and histhandler(=histcreator)

#----------------------------------------------------------------------
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
class RHistsHandler(object):
    """handles all the objects for the analysis"""

    #----------------------------------------------------------------------
    def __init__(self, ptbins, etabins, alphas, huguestree, isMC,
                 nbinR=30, xminR=0., xmaxR=2., verbose=False, 
                 varnames=['Rbalancing','RMPF']):
        """Constructor"""
        self.isMC = isMC
        self.varnames = varnames
        self.histsnames = []
        self.verbose = verbose
        self.huguestree = huguestree
        self.ptbins, self.etabins, self.alphas, self.nbinR, self.xminR, self.xmaxR = ptbins, etabins, alphas, nbinR, xminR, xmaxR
        self.makeRhists()
        
    #----------------------------------------------------------------------
    def getHist(self, histname, alpha=None):
        """get the hist (or dict of hists if alpha not specified)"""
        if alpha == None:
            return getattr(self, histname)
        else:
            return getattr(self, histname)[alpha]
        
    #----------------------------------------------------------------------
    def printHists(self):
        """prints all the made Rhist"""
        for name in self.histsnames:
            alphadict = getattr(self, name)
            for alpha, hist in alphadict.iteritems():
                print hist.args
        
    #----------------------------------------------------------------------
    def makeRhists(self):
        """make the Rhists"""
        for etamin, etamax in self.etabins:
            for ptmin, ptmax in self.ptbins:
                for varname in self.varnames:
                    name = '_'.join([varname,
                                     'eta{eta}'.format(eta=int(etamax)),
                                     'pt{pt}'.format(pt=int(ptmin))
                                     ])            
                    setattr(self, name, {})
                    self.histsnames.append(name)
                    for alpha in self.alphas:
                        cond = ['Pt_photon>={ptmin}'.format(ptmin=int(ptmin)),
                                'Pt_photon<{ptmax}'.format(ptmax=int(ptmax)),
                                'passHLT_Photon{pt}==1'.format(pt=findHLTPt(ptmin)),
                                'abs(Eta_photon)>={etamin}'.format(etamin=etamin),
                                'abs(Eta_photon)<{etamax}'.format(etamax=etamax),
                                'alpha < {alpha}'.format(alpha=alpha)]
                        cond = '('+' && '.join(cond)+')'
                        if self.isMC:
                            cond = cond+'*Tot_weight'
                        else:
                            cond = cond+'*1'
                        
                        histname = name + 'alpha{alpha}'.format(alpha=int(alpha*10))
                        histhandler = HistCreator(self.huguestree, varname, self.nbinR, self.xminR,
                                                  self.xmaxR, cond, histname)
                        histhandler.hist.Sumw2()
                        histhandler.args = {'ptmin':ptmin,
                                            'ptmax':ptmax,
                                            'etamin':etamin,
                                            'etamax':etamax,
                                            'varname':varname,
                                            'alpha':alpha}
                        getattr(self, name)[alpha] = histhandler
        if self.verbose==True:
            self.printHists()
                
    #----------------------------------------------------------------------
    def computeMeanAndRMS(self, percentIntegralmean = 0.985, percentIntegralrms = 0.985):
        """for each R histogram, computes the mean and RMS for a centered protion of the hist"""
        for name in self.histsnames:
            alphadict = getattr(self, name)
            for alpha, histh in alphadict.iteritems():
                integral = histh.hist.Integral()
                maxbin = histh.hist.GetMaximumBin()
                newhistmean = TH1F(name+'_mean'+ '_alpha{alpha}'.format(alpha=int(alpha*10)),
                                   name+'_mean'+ 'alpha{alpha}'.format(alpha=int(alpha*10)),
                                   self.nbinR,
                                   self.xminR,
                                   self.xmaxR)
                newhistrms = TH1F(name+'_rms'+ '_alpha{alpha}'.format(alpha=int(alpha*10)),
                                  name+'_rms'+ '_alpha{alpha}'.format(alpha=int(alpha*10)),
                                  self.nbinR,
                                  self.xminR,
                                  self.xmaxR)
                for i in range(maxbin):
                    if newhistmean.Integral() >= (integral * percentIntegralmean):
                        break
                    newhistmean.SetBinContent(maxbin+i,histh.hist.GetBinContent(maxbin+i))
                    newhistmean.SetBinContent(maxbin-i,histh.hist.GetBinContent(maxbin-i))
                for i in range(maxbin):
                    if newhistrms.Integral() >= (integral * percentIntegralrms):
                        break
                    newhistrms.SetBinContent(maxbin+i,histh.hist.GetBinContent(maxbin+i))
                    newhistrms.SetBinContent(maxbin-i,histh.hist.GetBinContent(maxbin-i))
                histh.mean = newhistmean.GetMean()
                histh.meanerr = newhistmean.GetMeanError()
                histh.rms = newhistmean.GetRMS()
                histh.rmserr = newhistmean.GetRMSError()
                
    #----------------------------------------------------------------------
    def extrapolateR(self):
        """extrapolates R to alpha->0, adds the results as hists['R0']"""
        for name in self.histsnames:
            alphadict = self.getHist(name)
            x, y = [], []
            for alpha, hist in alphadict.iteritems():
                x.append(alpha)
                y.append(hist.mean)
            graph = TGraph(len(x),array('d',x),array('d',y))
            func = TF1(name+'func','([0]*x)+[1]',0.,1.)
            graph.Fit(func,'QN')
            alphadict['R0']=func.GetParameter(1)