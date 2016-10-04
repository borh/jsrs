# Setup Notes

## Downloading Prerequisites

Download `lazy.mat`, `lazy.tools`, and `lazy.mdpref` from <http://www.ms.hum.titech.ac.jp/Rpackages.html>.

Unzip all packages before proceeding to the next step.

## Installing Prerequisites

```bash
curl -O http://www.ms.hum.titech.ac.jp/mayekawadocs/Rpackages/lazy.mat_0.1.2.zip
curl -O http://www.ms.hum.titech.ac.jp/mayekawadocs/Rpackages/lazy.tools_0.1.2.zip
curl -O http://www.ms.hum.titech.ac.jp/mayekawadocs/Rpackages/lazy.mdpref_0.1.2.zip
unzip -x lazy.mat_0.1.2.zip
unzip -x lazy.tools_0.1.2.zip
unzip -x lazy.mdpref_0.1.2.zip
Rscript -e "install.packages('naturalsort')"
R CMD INSTALL lazy.mat
R CMD INSTALL lazy.tools
R CMD INSTALL lazy.mdpref
Rscript -e "source(\"http://bioconductor.org/biocLite.R\"); biocLite(\"pcaMethods\")"
```
