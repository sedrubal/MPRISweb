SVGS := ${wildcard *.svg}
PNGS := ${SVGS:.svg=.png}

all: $(PNGS)

%.png: %.svg
	inkscape --export-png=$@ $<

clean:
	rm -vf $(PNGS)

.PHONY: all clean
