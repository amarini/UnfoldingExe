import ROOT
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

#random number generator
rand = ROOT.TRandom3(123456)


Nbins=30
resolution= .4
fluct = 1.0

gen  = ROOT.TH1D("truth","truth",Nbins,0,10)
reco = ROOT.TH1D("measured","measured",Nbins,0,10)
resp = ROOT.TH2D("resp","resp",Nbins,0,10,Nbins,0,10) # x= reco, y= truth


for i in range(0,gen.GetNbinsX()):
	x=gen.GetBinCenter(i+1)
	y=0.6*ROOT.TMath.Gaus(x,4,1,True) + 0.4*ROOT.TMath.Gaus(x,6.5,0.8,True)
	y*= 1000 ## n. of total events
	gen.SetBinContent(i+1,y)

## construct matrix
for i in range(0,gen.GetNbinsX() ):
  for j in range(0,reco.GetNbinsX() ):
	x=gen.GetBinCenter(i+1)
	y=reco.GetBinCenter(j+1)
	z=ROOT.TMath.Gaus(x-y,0,resolution)
	resp.SetBinContent(i+1,j+1,z )

## Normalize the matrix -- x=reco, y=truth
for j in range(0,reco.GetNbinsX() ):
  s=0
  for i in range(0,gen.GetNbinsX() ):
	c = resp.GetBinContent(j+1,i+1 )
	s += c
  for i in range(0,gen.GetNbinsX() ):
	c = resp.GetBinContent(j+1,i+1 )
	resp.SetBinContent(j+1,i+1,c / s )

## smear
for j in range(0,reco.GetNbinsX() ):
  s=0
  for i in range(0,gen.GetNbinsX() ):
  	g = gen.GetBinContent(i+1)
	fact = resp.GetBinContent(j+1,i+1 ) ###
	c = reco.GetBinContent(j+1);
	reco.SetBinContent( j+1, c + fact *  g ) 
	s += fact
  #c = reco.GetBinContent(j+1)  ## matrix is already norm
  #reco.SetBinContent(j+1, c/s )  ## normalize to the sum of gen I have

reco_fluct = reco.Clone("reco-fluct")
for j in range(0,reco.GetNbinsX() ):
	c=reco_fluct.GetBinContent(j+1)
	if c<0 : print "Warning: negative bin content!"
	newc= rand.Gaus(c,fluct)
	if(newc<0) : newc=0
	reco_fluct . SetBinContent(j+1, newc ) ##eccoc
#plot

## save as txt
txt = open("matrix.txt","w")
print >> txt, "## Response matrix (x=reco, y=truth), numbering starts from 1"
for j in range(0,reco.GetNbinsX() ):
  for i in range(0,gen.GetNbinsX() ):
	  print >> txt, i+1, j+1, resp.GetBinContent(i+1,j+1)
txt.close()

txt = open("reco.txt","w")
print >> txt, "## reconstructed distribution, no fluctuations, numbering starts from 1"
for j in range(0,reco.GetNbinsX() ):
	  print >> txt, j+1, reco.GetBinContent(j+1)
txt.close()

txt = open("reco_fluct.txt","w")
print >> txt, "## reconstructed distribution, gaus fluctuations, numbering starts from 1"
for j in range(0,reco.GetNbinsX() ):
	  print >> txt, j+1, reco_fluct.GetBinContent(j+1)
txt.close()

txt = open("gen.txt","w")
print >> txt, "## generated distribution, numbering starts from 1"
for i in range(0,gen.GetNbinsX() ):
	  print >> txt, i+1, gen.GetBinContent(i+1)
txt.close()


def SetCanvasStyle(canv):
	canv.SetLeftMargin(0.15)
	canv.SetRightMargin(0.05)

def SetLegendStyle(leg):
	leg.SetTextSize(0.03)
	leg.SetBorderSize(0)
	leg.SetFillStyle(0)

############################### DRAW GEN+RECO #########################
canv = ROOT.TCanvas("c1","c1",800,800)
if True:
	SetCanvasStyle(canv)
	gen.GetXaxis().SetTitle("x")
	gen.GetYaxis().SetTitleOffset(1.5)
	gen.GetYaxis().SetTitle("events")
	reco.SetLineColor(ROOT.kRed+2)
	reco_fluct.SetLineColor(ROOT.kGreen+2)
gen.Draw("AXIS")
gen.Draw("AXIS X+ Y+ SAME")
gen.Draw("HIST SAME")
reco.Draw("HIST SAME")

if True:
	leg = ROOT.TLegend(0.40,.30,.70,.47)
	SetLegendStyle(leg)
	leg.AddEntry(gen,"truth")
	leg.AddEntry(reco,"measured")
	leg.Draw()

canv.SaveAs("gen-reco.pdf")

############################### DRAW RECO + RECO-POISSON #########################
reco.Draw("HIST")
reco_fluct.Draw("HIST SAME")
if True:
	leg = ROOT.TLegend(0.40,.30,.70,.47)
	SetLegendStyle(leg)
	leg.AddEntry(reco,"measured (no fluctuations)")
	leg.AddEntry(reco_fluct,"measured (gaus fluctuations)")
	leg.Draw()
canv.SaveAs("reco.pdf")

############################### DRAW RESPT #########################
canv2 = ROOT.TCanvas("c2","c2",800,800)
if True:
	SetCanvasStyle(canv2)
	resp.GetXaxis().SetTitle("truth")
	resp.GetYaxis().SetTitle("measured")
	resp.GetYaxis().SetTitleOffset(1.5)
resp.Draw("AXIS")
resp.Draw("AXIS X+ Y+ SAME")
resp.Draw("BOX SAME")
canv2.SaveAs("respt.pdf")

########
fExe = ROOT.TFile.Open("Exe.root","RECREATE")
fExe.cd()

reco.Write()
reco_fluct.Write()
resp.Write()

fSolution = ROOT.TFile.Open("Solution.root","RECREATE")
reco.Write()
reco_fluct.Write()
resp.Write()
gen.Write()

############### Load RooUnfold ###############

ROOT.gSystem.Load("${HOME}/Downloads/RooUnfold-1.1.1/libRooUnfold.so")
##  prepare the response matrix
# assume a flat prior
R = ROOT.RooUnfoldResponse(None,None,resp)
u = ROOT.RooUnfoldInvert(R,reco)
u.SetName("unfolder1")
h = u.Hreco(ROOT.RooUnfold.kNone) 
h.SetName("unfold")

## for meaningful errors
for j in range(0,reco.GetNbinsX() ):
	reco_fluct.SetBinError(j+1,fluct)

u2 = ROOT.RooUnfoldInvert(R,reco_fluct)
u2.SetName("unfolder2")
u2.SetNToys(1000)
h2 = u2.Hreco( ROOT.RooUnfold.kCovToy)##  error propagation down with toys
h2.SetName("unfold2")

h.SetMarkerStyle(20)
h.SetMarkerColor(ROOT.kBlack)
h.SetLineColor(ROOT.kBlack)
h2.SetMarkerStyle(24)
h2.SetMarkerColor(ROOT.kRed+2)
h2.SetLineColor(ROOT.kRed+2)

canv3 =ROOT.TCanvas("c3","c3",800,800)
SetCanvasStyle(canv3)
gen.Draw("HIST")
h.Draw("P SAME")
h2.Draw("PE SAME")

print "H2 MIN=",h2.GetMinimum()," MAX=",h2.GetMaximum()

gen.GetYaxis().SetRangeUser(-200,500)
if True:
	#leg = ROOT.TLegend(0.40,.30,.70,.47)
	leg = ROOT.TLegend(0.40,.15,.70,.35)
	SetLegendStyle(leg)
	leg.AddEntry(gen,"generated")
	leg.AddEntry(h,"unfolded (no fluct)")
	leg.AddEntry(h2,"unfolded (gaus fluct)")
	leg.Draw()

canv3.SaveAs("gen-unfold.pdf")

##################### UNFOLDING STUDIES###########
histos=[]
gooderrors=[]
colors=[ROOT.kRed+2,ROOT.kRed,ROOT.kRed-2,ROOT.kBlue-2, ROOT.kBlue,ROOT.kBlue+2,ROOT.kGreen+2,ROOT.kGreen,ROOT.kGreen-2, ROOT.kMagenta-2,ROOT.kMagenta,ROOT.kMagenta+2]
canv4 = ROOT.TCanvas("c4","c4",800,800)
SetCanvasStyle(canv4)
reco_fluct.Draw("HIST")
reco_fluct.SetLineStyle(3)
reco_fluct.GetYaxis().SetRangeUser(-50,450)

if True:
	leg = ROOT.TLegend(0.64,.55,.95,.90)
	SetLegendStyle(leg)

for reg in range(0,Nbins/2):
	u = ROOT.RooUnfoldSvd(R,reco_fluct, 2*reg )
	h = u.Hreco(ROOT.RooUnfold.kCovToy) 
	h.SetName( "unfoldSvd_%d"%reg )
	c=colors.pop()
	colors = [c] + colors
	h.SetLineColor( c )
	h.SetMarkerColor( c )
	histos.append( h )
	gooderrors.append( h )
	h.Draw("PE SAME")
	leg.AddEntry(h,h.GetName() )

leg.Draw()
canv4.SaveAs("unfold-svd-reg.pdf")

canv5 = ROOT.TCanvas("c5","c5",800,800)
SetCanvasStyle(canv5)

u=ROOT.RooUnfoldSvd(R,reco_fluct, 30 )
u.Hreco(ROOT.RooUnfold.kNone)
print "Check ->",u,"->",u.Impl(),"->",u.Impl().GetD()
h=u.Impl().GetD()
h.Draw()

canv5.SaveAs("unfold-svd-ddistr.pdf")


canv6 = ROOT.TCanvas("c6","c6",800,800)
SetCanvasStyle(canv6)
reco_fluct.Draw("HIST")
if True:
	leg = ROOT.TLegend(0.64,.55,.95,.90)
	SetLegendStyle(leg)

for reg in [1,5,10,100,1000,10000]:
	u = ROOT.RooUnfoldBayes(R,reco_fluct,reg)
	if reg< 15:
		h = u.Hreco(ROOT.RooUnfold.kCovToy)
		gooderrors.append( h )
	else:
		h = u.Hreco(ROOT.RooUnfold.kNone)
	h.SetName( "unfoldBayes_%d"%reg )
	c=colors.pop()
	colors=[c]+colors
	h.SetLineColor( c )
	h.SetMarkerColor( c )
	histos.append( h )
	if reg< 15:
		h.Draw("PE SAME")
	else:
		h.Draw("HIST SAME")
	leg.AddEntry(h,h.GetName() )
leg.Draw()

canv6.SaveAs("unfold-bayes-reg.pdf")

########### Draw Relative error -before -after unfolding
canv7 = ROOT.TCanvas("c7","c7",800,800)
SetCanvasStyle(canv7)
axis=ROOT.TH1D("axis","axis",Nbins,0,10)
axis.Draw("AXIS")
axis.GetYaxis().SetRangeUser(0,10)
if True:
	leg = ROOT.TLegend(0.64,.55,.95,.90)
	SetLegendStyle(leg)
for h in gooderrors:
	for b in range(0,h.GetNbinsX()):
		e = h.GetBinError(b+1)
		e2= reco_fluct.GetBinError(b+1)
		h.SetBinContent( b+1, e/e2)
	h.Draw("HIST SAME")
	leg.AddEntry(h,h.GetName() )
leg.Draw()
canv7.SaveAs("unfold-error-reg.pdf")
raw_input("ok?")
