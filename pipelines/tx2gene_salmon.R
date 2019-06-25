args <- commandArgs(trailingOnly = TRUE)
DATADIR <- file.path(getwd(), args[1]) 
QUANTDIR <- file.path(getwd(), args[2])                      

library(readr)
library(erer)

#load file conatining mapping of transcripts to genes
tx2gene <- read_csv(file.path(getwd(), "tx2gene.csv"))
head(tx2gene)

#find quant files from salmon
files <- Sys.glob(file.path(QUANTDIR,'salmon_output/SRR*','quant.txt'))
paths <- strsplit(files, '/')
samples <- sapply(paths, "[[", length(paths[[1]])-1)
names(files) <- samples

cat('Exporting txi files to:', QUANTDIR, '\n' )
setwd(QUANTDIR)
## import transcript-level estimates
library(tximport)
txi <- tximport(files, type="salmon", tx2gene=tx2gene, abundanceCol="TPM", countsFromAbundance= "no")
write.csv(as.data.frame(txi),file="txi.csv")
#scaledTPM = TPM * sum(counts) for each sample
txi_scaledTPM <- tximport(files, type="salmon", tx2gene=tx2gene, abundanceCol="TPM",countsFromAbundance= "scaledTPM")
write.csv(as.data.frame(txi_scaledTPM),file="txi_scaledTPM.csv")
#additionally scaled using the average transcript length over samples and the library size (lengthScaledTPM)
txi_lengthScaledTPM <- tximport(files, type="salmon", tx2gene=tx2gene, abundanceCol="TPM",countsFromAbundance= "lengthScaledTPM")
write.csv(as.data.frame(txi_lengthScaledTPM),file="txi_lengthScaledTPM.csv")

names(txi)
head(txi$counts)

#sessionInfo()