import ROOT
ROOT.gSystem.Load("${HOME}/Downloads/RooUnfold-1.1.1/libRooUnfold.so")
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

# I need a defined defition of float/double ...
from array import array

#random number generator
rand = ROOT.TRandom3(123456)

### Create a tree
fExe = ROOT.TFile.Open("Exe2.root","RECREATE")
t = ROOT.TTree("events","events")

l1 = {}
l2 = {}

l1['Pt'] 	= array('f',[0])
l1['Eta'] 	= array('f',[0])

l2['Pt'] 	= array('f',[0])
l2['Eta'] 	= array('f',[0])

event = {}
event["weight"]	= array('f',[0])
event["sf1" ] 	= array('f',[0]) ## we describe them but not give
event["sf2" ] 	= array('f',[0])
event["npv"] 	= array('f',[0])
event["weight"]	= array('f',[0])

### define branches

t.Branch("lep1Pt", l1['Pt'], "lep1Pt/F")
t.Branch("lep1Eta", l1['Eta'], "lep1Eta/F")
t.Branch("lep2Pt", l2['Pt'], "lep2Pt/F")
t.Branch("lep2Eta", l2['Eta'], "lep2Eta/F")
t.Branch("weight", event['weight'],"weight/F")
t.Branch("npv",event["npv"],"npv/F")
#we can give the sf in a table

#total number of entries
Nentries = 10000

def ScaleFactor(pt,eta):
	if eta < -2 and pt <50 :  return 1.3
	if eta < -2 : return 0.9
	if eta < 0  and pt <50 : return 1.1
	if eta <0 : return 1
	if eta <2 and pt <50: return 0.8
	if eta <2  : return 1.2
	return 1.4

def Rejection(pt):
	if pt <10 : return 10
	if pt < 20: return 5
	if pt <50 : return 2
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

def PuWeight(npv):
	ABC

# ~ pt
fPt = ROOT.TF1("f1","TMath::Power(x,-5.2)",0,200);
# ~ eta
fY = ROOT.TF1("f2","-5*x*x + 5", -5,5)
# use fY.GetRandom()
#virtual void 	Sphere (Double_t &x, Double_t &y, Double_t &z, Double_t r)
# and then boost inverse

for i in Nentries:
	#generate pt1	
	l1['Pt'] = rand.
	#generate pt2
	#generate eta1
	#generate eta2
	#efficiency is function of npv ;-)
