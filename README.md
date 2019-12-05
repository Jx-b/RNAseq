# RNAseq
Tools for RNAseq analysis in python

_NB: This repository is a collection of scripts and notebooks for RNA seq analysis developped for my personnal use._

My objective in this repository is to use python whenever possible, however, most of the differential gene analysis tools are currently developed in R. In the current version of the RNAseq pipeline I have used the [characteristic direction method](http://www.maayanlab.net/CD/) developed by the Ma'ayan lab, which is available in python but I also made available notebooks in R using [edgeR](https://bioconductor.org/packages/release/bioc/html/edgeR.html), [limma-voom](https://bioconductor.org/packages/release/bioc/html/limma.html) and [sleuth](https://pachterlab.github.io/sleuth/about). In future versions of the pipeline, those will be integrated in python using [rpy2](https://rpy2.readthedocs.io/en/version_2.8.x/). Alternatively, edgeR might be integrated using the [edgePy package](https://github.com/r-bioinformatics/edgePy) currently under development.
