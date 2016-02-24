# Setup Notes

## Downloading Prerequisites

Download `lazy.mat`, `lazy.tools`, and `lazy.mdpref` from <http://www.ms.hum.titech.ac.jp/Rpackages.html>.

Unzip all packages before proceeding to the next step.

## Installing Prerequisites

```bash
Rscript -e "install.packages('naturalsort')" 
R CMD INSTALL lazy.mat
R CMD INSTALL lazy.tools
R CMD INSTALL lazy.mdpref
```
