import ROOT
ROOT.gSystem.Load("${HOME}/Downloads/RooUnfold-1.1.1/libRooUnfold.so")
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

# I need a defined defition of float/double ...
from array import array

#random number generator
rand = ROOT.TRandom3(1234567)

### Create a tree
fSol = ROOT.TFile.Open("Sol2.root","RECREATE")
hGen = ROOT.TH1D("gen","gen",100,0,100)

fExe = ROOT.TFile.Open("Exe2.root","RECREATE")
t = ROOT.TTree("events","events")
hData = ROOT.TH1D("data","data",100,0,100)

l1 = {}
l2 = {}

ROOT.gROOT.ProcessLine('struct lepton{ \
		float Pt;       \
		float Eta;       \
		float Phi;       \
		float PtReco;       \
		float EtaReco;       \
		float PhiReco;       \
		} l1,l2;')

ROOT.gROOT.ProcessLine('struct variables { \
		float weight ; \
		float sf1 ; \
		float sf2 ; \
		float npv ; \
		} event ; ')

from ROOT import lepton, l1, l2;
from ROOT import variables, event;


### define branches

t.Branch("lep1PtTruth" , ROOT.AddressOf(l1,'Pt'), "lep1PtTruth/F")
t.Branch("lep1EtaTruth", ROOT.AddressOf(l1,'Eta')	, "lep1EtaTruth/F")
t.Branch("lep1PhiTruth", ROOT.AddressOf(l1,'Phi')	, "lep1PhiTruth/F")
t.Branch("lep2PtTruth" , ROOT.AddressOf(l2,'Pt'  ) , "lep2PtTruth/F")
t.Branch("lep2EtaTruth", ROOT.AddressOf(l2,'Eta')	, "lep2EtaTruth/F")
t.Branch("lep2PhiTruth", ROOT.AddressOf(l2,'Phi')	, "lep2PhiTruth/F")

t.Branch("lep1PtReco" ,  ROOT.AddressOf(l1,'PtReco'), "lep1PtReco/F")
t.Branch("lep1EtaReco",  ROOT.AddressOf(l1,'EtaReco'), "lep1EtaReco/F")
t.Branch("lep1PhiReco",  ROOT.AddressOf(l1,'PhiReco'), "lep1PhiReco/F")
t.Branch("lep2PtReco" ,  ROOT.AddressOf(l2,'PtReco'), "lep2PtReco/F")
t.Branch("lep2EtaReco",  ROOT.AddressOf(l2,'EtaReco'), "lep2EtaReco/F")
t.Branch("lep2PhiReco",  ROOT.AddressOf(l2,'PhiReco'), "lep2PhiReco/F")

t.Branch("weight", ROOT.AddressOf(event,'weight'),"weight/F")
#t.Branch("npv",   ROOT.AddressOf(event,'npv'),"npv/F")

#we can give the sf in a table

#total number of entries
Nentries = 100000

def EfficiencyMC(pt, eta, npv = 0):
	if pt < 10: return 0.8
	if pt < 20 and eta <2: return .9
	if pt < 20 : return .95
	return .99

def EfficiencyData(pt,eta,npv=0):
	#
	if pt < 10: return 0.72
	if pt < 20 and eta <2: return 0.72
	if pt < 20 : return .9025
	#
	if eta < -2  and pt <50 :  return 0.9207
	if eta < -2 : return 0.8712
	if eta < 0  and pt <50 : return .8811
	if eta < 0 : return .99
	if eta < 2 and pt <50: return 0.96921
	if eta <2  : return .9999
	# eif eta (2.5)
	return .9504


def PrintScaleFactor():
	ptBound=[0,10,20,50, 10000]
	etaBound=[-5,-2,0,2,5]
	txt=open("scalefactors.txt","w")
	print >>txt, "## pt1 pt2 eta1 eta2 sf"
	for iPt in range(0, len(ptBound) -1):
	   for iEta in range(0,len(etaBound)-1):
		print >>txt, ptBound[iPt],ptBound[iPt+1],
		print >>txt, etaBound[iEta],etaBound[iEta+1],
		pt= (ptBound[iPt] + ptBound[iPt+1])/2
		eta= (etaBound[iEta] + etaBound[iEta+1])/2
		npv=0
		print >>txt, EfficiencyData(pt,eta,npv) / EfficiencyMC(pt,eta,npv);

def Rejection(pt):
	if pt <10 : return 10
	if pt < 20: return 5.7
	if pt <50 : return 2.4
	return 1

def PtSmear(pt,eta):
	''' small bias in the pt distribution. It is able to correct for it. '''
	if eta <1:
		return rand.Gaus(pt -.1 , 1)
	if eta >1:
		return rand.Gaus(pt + .5 ,3)

def EtaSmear(pt,eta):
	## eta is quite precise
	return rand.Gaus(eta,0.1)

def PhiSmear(phi):
	## eta is quite precise
	return rand.Gaus(phi,0.1)


def PuWeight(npv):
	ABC

# ~ pt
#fPt = ROOT.TF1("f1","TMath::Power(x,-5.2)",0,200);
fPt = ROOT.TF1("f1","1e+6*TMath::Power(x,-3)*TMath::Exp(-50./x)",0,200);
# ~ eta
fY = ROOT.TF1("f2","-x*x + 25", -5,5)
# use fY.GetRandom()
#virtual void 	Sphere (Double_t &x, Double_t &y, Double_t &z, Double_t r)
# and then boost inverse

x = array('d',[0])
y = array('d',[0])
z = array('d',[0])

for iEntry in range(0,Nentries):
	print "\rReading entry","%5d"%(iEntry),"/",Nentries, "--","%.2f"%(float(iEntry)/Nentries * 100.),"%",
	#generate pt1	
	llPt = fPt.GetRandom();
	llEta = fY.GetRandom();
	n = Rejection(llPt)
	## random distribution between 0 - 1
	## accept 1 every N (with N also fractional)
	accept = ( rand.Uniform(1) * n < 1)
	event.weight = n

	# uniform distribution
	llPhi = rand.Uniform(1) *2.0*3.1415 - 3.1415;
	llM=91;

	Z= ROOT.TLorentzVector()

	Z.SetPtEtaPhiM(llPt, llEta, llPhi , llM)

	b = Z.BoostVector() # get the boost vector
	
	lA = ROOT.TLorentzVector()
	lB = ROOT.TLorentzVector()
	## sphere
	rand.Sphere(x,y,z,1) ## uniform decay in the center of mass rest frame
	mMu = 0.105
	lA.SetXYZM( x[0]* llM/2.0, y[0]*llM/2.0, z[0]*llM/2.0, mMu);
	lB.SetXYZM( -x[0]* llM/2.0, -y[0]*llM/2.0, -z[0]*llM/2.0, mMu);
	lA.Boost(b);	
	lB.Boost(b);
	
	## print "Event",iEntry,":"
	## print "\t x,y,z",x[0],y[0],z[0]
	## print "\t Z Pt=",llPt
	## print "\t Z Phi=",llPhi
	## print "\t Z Eta=",llEta
	## print "\t lx,ly,ly", lA.Px(), lA.Py(),lA.Pz()
	## print "\t lpt,leta,lphi",lA.Pt(),lA.Eta(),lA.Phi()

	#
	if lA.Pt() > lB.Pt() :
		l1.Pt  = lA.Pt()
		l1.Eta = lA.Eta();
		l1.Phi = lA.Phi()
		l2.Pt  = lB.Pt()
		l2.Eta = lB.Eta();
		l2.Phi = lB.Phi()
	else:
		l2.Pt  = lA.Pt()
		l2.Eta = lA.Eta();
		l2.Phi = lA.Phi()
		l1.Pt  = lB.Pt()
		l1.Eta = lB.Eta();
		l1.Phi = lB.Phi()

	event.npv = rand.Poisson(10)
	#efficiency is function of npv ;-)
	lAPtReco = PtSmear(l1.Pt,l1.Eta)
	lAEtaReco = EtaSmear(l1.Pt,l1.Eta)
	lAPhiReco = PhiSmear(l1.Phi)

	lBPtReco = PtSmear(l2.Pt,l2.Eta)
	lBEtaReco = EtaSmear(l2.Pt,l2.Eta)
	lBPhiReco = PhiSmear(l2.Phi)

	# we will apply sf on the reco level, easier
	#e1MC= EfficiencyMC(l1.Pt,l1.Eta,event.npv) 
	#e2MC= EfficiencyMC(l2.Pt,l2.Eta,event.npv)
	#e1D= EfficiencyData(l1.Pt,l1.Eta,event.npv) 
	#e2D= EfficiencyData(l2.Pt,l2.Eta,event.npv)

	e1MC= EfficiencyMC(lAPtReco,lAEtaReco,event.npv) 
	e2MC= EfficiencyMC(lBPtReco,lBEtaReco,event.npv)
	e1D= EfficiencyData(lAPtReco,lAEtaReco,event.npv) 
	e2D= EfficiencyData(lBPtReco,lBEtaReco,event.npv)


	##
	isReco1=False	
	isReco2=False
	if rand.Uniform() < e1MC : isReco1=True
	if rand.Uniform() < e2MC : isReco2=True
	
	isData1 = False
	isData2 = False
	if rand.Uniform() < e1D : isData1 = True
	if rand.Uniform() < e2D : isData2 = True

	#l1.PtReco
	if not isReco1:
		lAPtReco = 0
		lAEtaReco = 0
		lAPhiReco = 0

	if not isReco2:
		lBPtReco = 0 ;
		lBEtaReco = 0 ;
		lBPhiReco = 0 ;

	if lAPtReco > lBPtReco:
		l1.PtReco = lAPtReco
		l1.EtaReco = lAEtaReco
		l1.PhiReco = lAPhiReco
		l2.PtReco = lBPtReco
		l2.EtaReco = lBEtaReco
		l2.PhiReco = lBPhiReco
	else:
		l2.PtReco = lAPtReco
		l2.EtaReco = lAEtaReco
		l2.PhiReco = lAPhiReco
		l1.PtReco = lBPtReco
		l1.EtaReco = lBEtaReco
		l1.PhiReco = lBPhiReco

	## fill data distribution
	lR1 = ROOT.TLorentzVector()
	lR1.SetPtEtaPhiM(l1.PtReco,l1.EtaReco,l1.PhiReco,mMu)
	lR2 = ROOT.TLorentzVector()
	lR2.SetPtEtaPhiM(l2.PtReco,l2.EtaReco,l2.PhiReco,mMu)

	llR = lR1 + lR2

	## fill if accepted
	if accept: 
		t.Fill()

	## before weights
	if l1.Pt >15 and l2.Pt > 15 and abs(l1.Eta ) <2.5 and abs(l2.Eta)<2.5 :
		hGen.Fill(llPt)

	if isData1 and isData2:
		lAPtReco = PtSmear(l1.Pt,l1.Eta)
		lAEtaReco = EtaSmear(l1.Pt,l1.Eta)
		lAPhiReco = PhiSmear(l1.Phi)
		lBPtReco = PtSmear(l2.Pt,l2.Eta)
		lBEtaReco = EtaSmear(l2.Pt,l2.Eta)
		lBPhiReco = PhiSmear(l2.Phi)
		lR1 = ROOT.TLorentzVector()
		lR1.SetPtEtaPhiM(lAPtReco,lAEtaReco,lAPhiReco,mMu)
		lR2 = ROOT.TLorentzVector()
		lR2.SetPtEtaPhiM(lBPtReco,lBEtaReco,lBPhiReco,mMu)
		llR = lR1 + lR2

		## additional selection
		if (lR1.Pt() > 15 and lR2.Pt() >15  and abs(lR1.Eta()) <2.5 and abs(lR2.Eta())<2.5 ):
			hData.Fill( llR.Pt() )

	## fill gen-truth, with the truth selection, and without cuts

## create a background TODO

#put a bump/bias in data ?  
fSol.cd()
hGen_noBump = hGen.Clone("gen_noBump")
hData_noBump = hData.Clone("data_noBump")

bEntries=Nentries/40
for iEntry in range(0,bEntries):
	print "\rBumping entry:","%5d"%(iEntry),"/",bEntries, "--","%.2f"%(float(iEntry)/bEntries * 100.),"%",
	llPt = rand.Gaus(70,5);
	llEta = fY.GetRandom();
	llPhi = rand.Uniform(1) *2.0*3.1415 - 3.1415;
	llM=91;
	Z= ROOT.TLorentzVector()
	Z.SetPtEtaPhiM(llPt, llEta, llPhi , llM)
	b = Z.BoostVector() # get the boost vector
	lA = ROOT.TLorentzVector()
	lB = ROOT.TLorentzVector()
	## sphere
	rand.Sphere(x,y,z,1) ## 
	mMu = 0.105
	lA.SetXYZM( x[0]* llM/2.0, y[0]*llM/2.0, z[0]*llM/2.0, mMu);
	lB.SetXYZM( -x[0]* llM/2.0, -y[0]*llM/2.0, -z[0]*llM/2.0, mMu);
	lA.Boost(b);	
	lB.Boost(b);
	if lA.Pt() > lB.Pt() :
		l1.Pt  = lA.Pt()
		l1.Eta = lA.Eta();
		l1.Phi = lA.Phi()
		l2.Pt  = lB.Pt()
		l2.Eta = lB.Eta();
		l2.Phi = lB.Phi()
	else:
		l2.Pt  = lA.Pt()
		l2.Eta = lA.Eta();
		l2.Phi = lA.Phi()
		l1.Pt  = lB.Pt()
		l1.Eta = lB.Eta();
		l1.Phi = lB.Phi()

	lAPtReco = PtSmear(l1.Pt,l1.Eta)
	lAEtaReco = EtaSmear(l1.Pt,l1.Eta)
	lAPhiReco = PhiSmear(l1.Phi)
	lBPtReco = PtSmear(l2.Pt,l2.Eta)
	lBEtaReco = EtaSmear(l2.Pt,l2.Eta)
	lBPhiReco = PhiSmear(l2.Phi)

	#e1D= EfficiencyData(l1.Pt,l1.Eta,event.npv) 
	#e2D= EfficiencyData(l2.Pt,l2.Eta,event.npv)

	e1D= EfficiencyData(lAPtReco,lAEtaReco,event.npv) 
	e2D= EfficiencyData(lBPtReco,lBEtaReco,event.npv)
	isData1 = False
	isData2 = False
	if rand.Uniform() < e1D : isData1 = True
	if rand.Uniform() < e2D : isData2 = True

	if l1.Pt >15 and l2.Pt > 15 and abs(l1.Eta ) <2.5 and abs(l2.Eta)<2.5 :
		hGen.Fill(llPt)

	if isData1 and isData2:
		lR1 = ROOT.TLorentzVector()
		lR1.SetPtEtaPhiM(lAPtReco,lAEtaReco,lAPhiReco,mMu)
		lR2 = ROOT.TLorentzVector()
		lR2.SetPtEtaPhiM(lBPtReco,lBEtaReco,lBPhiReco,mMu)
		llR = lR1 + lR2

		## additional selection
		if (lR1.Pt() > 15 and lR2.Pt() >15  and abs(lR1.Eta()) <2.5 and abs(lR2.Eta())<2.5 ):
			hData.Fill( llR.Pt() )

# smear data
for i in range(0,hData.GetNbinsX() +1): ## also overflow
	c= hData.GetBinContent( i+1)
	hData.SetBinContent(i+1,rand.Poisson(c) ) 
	hData.SetBinError(i+1, ROOT.TMath.Sqrt(hData.GetBinContent(i+1)) ) 

### Write and Close
fExe.cd()
t.Write()
hData.Write()
fExe.Close()

fSol.cd()
hGen.Write()
hGen_noBump.Write()
fSol.Close()


PrintScaleFactor()
