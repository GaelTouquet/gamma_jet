from ROOT import TFile
import numpy

def addbranch(tree):
    weight = numpy.zeros(1,numpy.float32)
    branch = tree.Branch("Tot_weight",
                          weight,
                          "Tot_weight/F")
    for event in tree:
        weight[0]= event.weight
        branch.Fill()


fil = TFile.Open('hugues.root')
tree = fil.Get('tree')
fil2 = TFile.Open('test.root','recreate')
tree2 = tree.CloneTree()
addbranch(tree2)
tree2.Write()
fil2.Close()

print 'ok'