args <- commandArgs(trailingOnly = TRUE)
OUTDIR <- file.path(getwd(), args[1]) 
GENOME <- file.path(getwd(), args[2]) 
QUANTDIR <- file.path(getwd(), args[3])                      

cat('Setting WORKDIR to:', OUTDIR, '\n' )
setwd(OUTDIR)

library(readr)
library(erer)

## generate 2-columns table to map transcript to gene from Gencode
if(!file.exists("tx2gene.csv")){
    library(GenomicFeatures)
    txdb <- makeTxDbFromGFF(file = GENOME)
    k <- keys(txdb, keytype = "TXNAME")
    tx2gene <- select(txdb, k, "GENEID", "TXNAME")
    head(tx2gene)
    write.csv(as.data.frame(tx2gene),file="tx2gene.csv", row.names=FALSE)
    #write.list(tx2gene, "tx2gene.gencode.v27.csv")
} else {
    tx2gene <- read_csv(file.path(getwd(), "tx2gene.csv"))
    head(tx2gene)
}
## generate 2-columns table to map transcript to gene from ENSEMBL
#library(EnsDb.Hsapiens.v79)
#txdf <- transcripts(EnsDb.Hsapiens.v79, return.type="DataFrame")
#tx2gene <- as.data.frame(txdf[,c("tx_id","gene_id")])

#find quant files from salmon
files <- Sys.glob(file.path(QUANTDIR,'salmon_output/SRR*','quant.sf'))
paths <- strsplit(files, '/')
samples <- sapply(paths, "[[", length(paths[[1]])-1)
names(files) <- samples

## import transcript-level estimates
library(tximport)
txi <- tximport(files, type="salmon", tx2gene=tx2gene, abundanceCol="TPM", countsFromAbundance= "no")
#scaledTPM = TPM * sum(counts) for each sample
txi_scaledTPM <- tximport(files, type="salmon", tx2gene=tx2gene, abundanceCol="TPM",countsFromAbundance= "scaledTPM")
#additionally scaled using the average transcript length over samples and the library size (lengthScaledTPM)
txi_lengthScaledTPM <- tximport(files, type="salmon", tx2gene=tx2gene, abundanceCol="TPM",countsFromAbundance= "lengthScaledTPM")

names(txi)
head(txi$counts)

write.csv(as.data.frame(txi),file="txi.csv")
write.csv(as.data.frame(txi_scaledTPM),file="txi_scaledTPM.csv")
write.csv(as.data.frame(txi_lengthScaledTPM),file="txi_lengthScaledTPM.csv")

sessionInfo()