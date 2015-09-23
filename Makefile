TEX=pdflatex
TEXFLAGS=--shell-escape -interaction nonstopmode
GARBAGE_EXT=aux bbl blg brf idx ilg ind log out pdf lof lot toc
EXE=UnfoldingExe
SOLUTION=UnfoldingSolution
TARGET=$(EXE).pdf $(SOLUTION).pdf

GARBAGE=$(foreach ext,$(GARBAGE_EXT),$(EXE).$(ext))
GARBAGE:=$(GARBAGE) $(foreach ext,$(GARBAGE_EXT),$(SOLUTION).$(ext))

.PHONY: all
all: $(EXE).pdf $(SOLUTION).pdf

$(EXE).pdf: $(EXE).bib $(EXE).tex difficulty.tex
	-$(TEX) --draftmode $(TEXFLAGS) $(EXE).tex
	bibtex $(EXE)
	-$(TEX) --draftmode $(TEXFLAGS) $(EXE).tex
	$(TEX) $(TEXFLAGS) $(EXE).tex
	@echo "----- DONE ------"

$(SOLUTION).pdf: $(SOLUTION).tex
	-$(TEX) --draftmode $(TEXFLAGS) $(SOLUTION).tex
	$(TEX) $(TEXFLAGS) $(SOLUTION).tex
	@echo "----- DONE ------"

.PHONY: clean
clean:
	-rm -v $(GARBAGE)

