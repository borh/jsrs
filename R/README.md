# Setup Notes

## Downloading Prerequisites

Download `lazy.mat`, `lazy.tools`, and `lazy.mdpref` from <http://mayekawa.in.coocan.jp/Rpackages.html>.

Unzip all packages before proceeding to the next step.

## Installing Prerequisites

```bash
curl -O http://mayekawa.in.coocan.jp/Rpackages/lazy.mat_0.1.3.zip
curl -O http://mayekawa.in.coocan.jp/Rpackages/lazy.tools_0.1.3.zip
curl -O http://mayekawa.in.coocan.jp/Rpackages/lazy.mdpref_0.1.2.zip
unzip -x lazy.mat_0.1.3.zip
unzip -x lazy.tools_0.1.3.zip
unzip -x lazy.mdpref_0.1.2.zip
Rscript -e "install.packages('naturalsort')"
R CMD INSTALL lazy.mat
R CMD INSTALL lazy.tools
R CMD INSTALL lazy.mdpref
Rscript -e "source(\"http://bioconductor.org/biocLite.R\"); biocLite(\"pcaMethods\")"
```
