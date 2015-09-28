import ROOT 
import sys,os


# read sf
sfTxt = open("scalefactors.txt")
sf = []
for line in sfTxt:
	l = line.split('#')[0].replace('\n','')
	if l == '' : continue
	parts= l.split()

	pt1=float(parts[0])
	pt2=float(parts[1])
	eta1=float(parts[2])
	eta2=float(parts[3])
	val = float(parts[4])

	sf.append( (pt1,pt2,eta1,eta2,val) )

## open root file
fRoot = ROOT.TFile.Open("Exe2.root")
t = fRoot.Get("events")
hData = fRoot.Get("data")

### save histos for RooResponse. 
#If you use the built in functions you need to set a complecate set of weights and counter weights to handle them properly
hReco =  hData.Clone("reco")
hTruth=  hData.Clone("truth")
hReco.Reset("ACE")
hTruth.Reset("ACE")
nb= hData.GetNbinsX()
xmin = hData.GetBinLowEdge(1)
xmax = hData.GetBinLowEdge(nb+1)
hMatrix = ROOT.TH2D("matrix","matrix",nb,xmin,xmax,nb,xmin,xmax)
muonMass = .105

## if sf weights are put also here
hTruthWrong1 = hTruth.Clone("TruthWrongWeights") ## no SF
hRecoWrong2 = hReco.Clone("RecoWrongWeights2") ## no weights at all
hTruthWrong2 = hTruth.Clone("TruthWrongWeights2") ## no weights at all
hMatrixWrong2 = hMatrix.Clone("MatrixWrongWeights2") ## no weights at all
## no weights at all


# construct response matrix
for iEntry in range(0,t.GetEntries()):
	print "\rReading entry","%5d"%(iEntry),"/",t.GetEntries(), "--","%.2f"%(float(iEntry)/t.GetEntries() * 100.),"%",
	sys.stdout.flush()
	t.GetEntry(iEntry)
	#implement gen selection
	isGen = t.lep1PtTruth >=15 and t.lep2PtTruth >= 15  and abs(t.lep1EtaTruth )<2.5 and abs(t.lep2EtaTruth) <2.5
	isReco = t.lep1PtReco >=15 and t.lep2PtReco >= 15  and abs(t.lep1EtaReco )<2.5 and abs(t.lep2EtaReco) <2.5

	mysf = 1.0

	for pt1,pt2,eta1,eta2,val in sf:
		if pt1 <= t.lep1PtTruth  and t.lep1PtTruth < pt2  \
			and eta1 <= t.lep1EtaTruth and t.lep1EtaTruth< eta2:
			mysf *=val
		if pt1 <= t.lep1PtTruth  and t.lep1PtTruth < pt2  \
			and eta1 <= t.lep2EtaTruth and t.lep2EtaTruth< eta2:
			mysf *=val
	
	if isGen:
		l1G = ROOT.TLorentzVector()
		l2G = ROOT.TLorentzVector()
		l1G.SetPtEtaPhiM(t.lep1PtTruth,t.lep1EtaTruth,t.lep1PhiTruth,muonMass)
		l2G.SetPtEtaPhiM(t.lep2PtTruth,t.lep2EtaTruth,t.lep2PhiTruth,muonMass)
		Z = l1G + l2G
		hTruth.Fill(Z.Pt(), t.weight ) # no sf
		hTruthWrong1.Fill(Z.Pt(), t.weight * mysf) # wrong, sf should not be here, it's like not applying them
		hTruthWrong2.Fill(Z.Pt() , 1.)
	if isReco:
		l1R = ROOT.TLorentzVector()
		l2R = ROOT.TLorentzVector()
		l1R.SetPtEtaPhiM(t.lep1PtReco,t.lep1EtaReco,t.lep1PhiReco,muonMass) # muon mass can be and it is assumed in the reconstruction
#open solution file
		l2R.SetPtEtaPhiM(t.lep2PtReco,t.lep2EtaReco,t.lep2PhiReco,muonMass) # muon mass can be and it is assumed in the reconstruction
		LL = l1R + l2R
		hReco.Fill( LL.Pt(), t.weight * mysf) 
		hRecoWrong2.Fill(LL.Pt() , 1.)

	if isGen and isReco:
		# Y is Gen
		hMatrix.Fill(LL.Pt(),Z.Pt(),t.weight*mysf)
		hMatrixWrong2.Fill(LL.Pt(),Z.Pt(),1.)

# construct RooResponse and unfold
ROOT.gSystem.Load("${HOME}/Downloads/RooUnfold-1.1.1/libRooUnfold.so")
R = ROOT.RooUnfoldResponse(hReco,hTruth,hMatrix)
u = ROOT.RooUnfoldBayes(R,hData,5)

#hUnfold = u.Hreco(ROOT.RooUnfold.kCovToy)
hUnfold = u.Hreco(ROOT.RooUnfold.kNone)
hUnfold.SetName("hUnfold")

### Wrong 1
R = ROOT.RooUnfoldResponse(hReco,hTruthWrong1,hMatrix)
u = ROOT.RooUnfoldBayes(R,hData,5)
hUnfoldWrong1 = u.Hreco(ROOT.RooUnfold.kNone)
## Wrong 2
R = ROOT.RooUnfoldResponse(hRecoWrong2,hTruthWrong2,hMatrixWrong2)
u = ROOT.RooUnfoldBayes(R,hData,5)
hUnfoldWrong2 = u.Hreco(ROOT.RooUnfold.kNone)

#draw
fSol = ROOT.TFile.Open("Sol2.root")
hGen = fSol.Get("gen")

c = ROOT.TCanvas()
hUnfold.SetMarkerStyle(20)
hData.SetMarkerStyle(24) ## prior unfolding
hGen.SetLineColor(ROOT.kRed) ## truth
hUnfoldWrong1.SetLineColor(ROOT.kGreen+2)
hUnfoldWrong1.SetLineStyle(7)

hUnfoldWrong2.SetLineColor(ROOT.kMagenta+2)
hUnfoldWrong2.SetLineStyle(7)

ymax = hGen.GetMaximum()
hGen.GetYaxis().SetRangeUser(0, ymax*1.4)

hGen.Draw("HIST")
hData.Draw("P SAME")
hUnfold.Draw("PSAME")
hUnfoldWrong1.Draw("HIST SAME")
hUnfoldWrong2.Draw("HIST SAME")

leg = ROOT.TLegend(.6,.5,.9,.9)
leg.AddEntry( hData,"data")
leg.AddEntry( hUnfold,"unfolded data")
leg.AddEntry( hGen,"truth")
leg.AddEntry( hUnfoldWrong1,"unfolded data (wrong, no sf)")
leg.AddEntry( hUnfoldWrong2,"unfolded data (wrong, no weights)")

leg.Draw()

raw_input("ok?")
c.SaveAs("unfolding2.pdf")


