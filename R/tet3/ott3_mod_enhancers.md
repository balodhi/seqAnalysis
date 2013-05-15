OMP-tTA / tetO-Tet3 5hmC/5mC enhancers
========================================================


```r
suppressPackageStartupMessages(source("~/src/seqAnalysis/R/profiles2.R"))
suppressPackageStartupMessages(source("~/src/seqAnalysis/R/image.R"))
suppressPackageStartupMessages(source("~/src/seqAnalysis/R/features.R"))
```


Make profiles
```
makeProfile2.allSamp("phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb.bed_W25F200_both_chr", data_type="rpkm/mean")
```

Plot OMP and O/TT3 5hmC

```r
plot2.several("phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb.bed_W25F200_both_chr", 
    "tt3_3_hmc", data_type = "rpkm/mean", cols = col2, fname = "manual", y.vals = c(0.2, 
        1))
```

```
## [1] "omp_hmc_120424_rpkm_mean"
## [1] "ott3_1_hmc_rpkm_mean"
```

![plot of chunk phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb.bed_W25F200_both_tt3_3_hmc](figure/phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb.bed_W25F200_both_tt3_3_hmc.png) 

```
## [1] 0.2 1.0
```



Heatmaps

```
positionMatrix.all("phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb.bed_W25F200_both_chr", data_type="rpkm/mean")
```

```r

omp.pos <- makeImage("omp_hmc_120424_rpkm", "phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb.bed_W25F200_both_chr", 
    data_type = "rpkm/mean", image = F)
```

```
## [1] "/media/storage2/analysis/profiles/norm/rpkm/mean/phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb.bed_W25F200_both_chr/images/omp_hmc_120424_rpkm"
```

```r
ott3.pos <- makeImage("ott3_1_hmc_rpkm", "phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb.bed_W25F200_both_chr", 
    data_type = "rpkm/mean", image = F)
```

```
## [1] "/media/storage2/analysis/profiles/norm/rpkm/mean/phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb.bed_W25F200_both_chr/images/ott3_1_hmc_rpkm"
```

```r

omp.pos.na <- which(is.na(omp.pos), arr.ind = TRUE)
omp.pos[omp.pos.na] <- 0
omp.pos.pc <- prcomp(omp.pos)
omp.pos.pred <- predict(omp.pos.pc, omp.pos)
omp.pos.pc1 <- omp.pos[order(-omp.pos.pred[, 1]), ]

ott3.pos.na <- which(is.na(ott3.pos), arr.ind = TRUE)
ott3.pos[ott3.pos.na] <- 0
ott3.pos.pc <- prcomp(ott3.pos)
ott3.pos.pred <- predict(ott3.pos.pc, ott3.pos)
ott3.pos.pc1 <- ott3.pos[order(ott3.pos.pred[, 1]), ]

ott3.pos.omp.pc1 <- ott3.pos[order(-omp.pos.pred[, 1]), ]
```



```r
# omp.pos.pc1 <- apply(t(omp.pos.pc1), 1, function(x)
# predict(loess(x~c(1:nrow(omp.pos.pc1)), span=.05))) omp.pos.pc1 <-
# t(apply(omp.pos.pc1, 1, function(x) predict(loess(x~c(1:400),
# span=.05))))

# ott3.pos.pc1 <- apply(t(ott3.pos.pc1), 1, function(x)
# predict(loess(x~c(1:nrow(ott3.pos.pc1)), span=.05))) ott3.pos.pc1 <-
# t(apply(ott3.pos.pc1, 1, function(x) predict(loess(x~c(1:400),
# span=.05))))
```



```r
MP.heat(omp.pos.pc1, average = 50, range = c(0, 1.5))
```

![plot of chunk phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb.bed_W25F200_both_chr_omp_hmc_order_omp_hmc_pc1](figure/phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb.bed_W25F200_both_chr_omp_hmc_order_omp_hmc_pc1.png) 



```r
MP.heat(ott3.pos.omp.pc1, average = 50, range = c(0, 1.5))
```

![plot of chunk phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb.bed_W25F200_both_chr_ott3_1_hmc_order_omp_hmc_pc1](figure/phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb.bed_W25F200_both_chr_ott3_1_hmc_order_omp_hmc_pc1.png) 



```r
MP.heat(ott3.pos.pc1, average = 50, range = c(0, 1))
```

![plot of chunk unnamed-chunk-4](figure/unnamed-chunk-4.png) 


Load closest genes

```r
rg <- read.delim("/seq/lib/roi/closest/refgene_nodup_closest_phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb.bed", 
    header = FALSE)
rna.1log2 <- readRDS("~/s2/analysis/rna/rdata/omp_ott3_rmrna_masked_uq_1log2.rds")
rna.1log2.rg <- na.omit(rna.1log2[match(rg[, 4], rna.1log2$gene), ])
rna.1log2.rg$enhancer.id <- rg[match(rna.1log2.rg$gene, rg[, 4]), 10]
```


Order RNA by enhancer order

```r
rna.1log2.rg.omp <- rna.1log2.rg[order(rg[match(rownames(omp.pos.pc1), rg[, 
    10]), 4]), ]
rna.1log2.rg.omp.c100 <- foreach(c = isplitRows(rna.1log2.rg.omp[, 2:4], chunks = 100), 
    .combine = "rbind") %do% apply(c, 2, mean, trim = 0.05)
rna.1log2.rg.omp.c100 <- as.data.frame(rna.1log2.rg.omp.c100)
rna.1log2.rg.omp.c100$index <- 100:1

rna.1log2.rg.omp.c100.boot <- foreach(c = isplitRows(rna.1log2.rg.omp[, c(2:4)], 
    chunks = 100), .combine = "rbind") %do% apply(c, 2, bootCI)
rna.1log2.rg.omp.c100 <- cbind(rna.1log2.rg.omp.c100, rna.1log2.rg.omp.c100.boot[seq(1, 
    nrow(rna.1log2.rg.omp.c100.boot), 2), ], rna.1log2.rg.omp.c100.boot[seq(2, 
    nrow(rna.1log2.rg.omp.c100.boot), 2), ])
colnames(rna.1log2.rg.omp.c100)[5:10] <- c("omp.lower", "ott3.lower", "ott3.omp.lower", 
    "omp.upper", "ott3.upper", "ott3.omp.upper")
```



```r
suppressWarnings(rna.1log2.rg.omp.c100$wilcox.FDR <- p.adjust(foreach(c = isplitRows(rna.1log2.rg.omp[, 
    2:4], chunks = 100), .combine = "rbind") %do% wilcox.test(c[, 3])$p.value, 
    method = "fdr"))
rna.1log2.rg.omp.c100$wilcox.FDR.05 <- cut(rna.1log2.rg.omp.c100$wilcox.FDR, 
    breaks = c(0, 0.05, 1))
```



```r
gg <- ggplot(rna.1log2.rg.omp.c100, aes(ott3.omp, index))
gg <- gg + geom_vline(xintercept = 0, color = "red")
gg <- gg + geom_errorbarh(aes(xmin = ott3.omp.lower, xmax = ott3.omp.upper), 
    height = 0, size = 0.1) + geom_point(aes(color = wilcox.FDR.05), size = 2) + 
    xlab("log2(FPKM + 1)") + ylab("") + theme(legend.position = "none", axis.text.y = element_blank()) + 
    labs(title = c("O/Tet3-OMP ratio RNA by OMP PC1")) + scale_color_manual(values = c("red", 
    "black"))
gg
```

![plot of chunk refgene_nodup_closest_phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb_omp_ott3_rmna_ratio](figure/refgene_nodup_closest_phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb_omp_ott3_rmna_ratio.png) 



### Mean 5hmC levels

```r
mk4.feat <- makeFeatureMatrix2("phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb.bed_chr", 
    set = "tt3_min", data_type = "rpkm/mean", transf = "sqrt")
```

```
## [1] "omp_hmc_120424_rpkm" "ott3_1_hmc_rpkm"     "ott3_2_hmc_rpkm"    
## [4] "omp_mc_rpkm"         "ott3_1_mc_rpkm"      "ott3_2_mc_rpkm"
```

```r
mk4.feat.nz <- mk4.feat[apply(mk4.feat, 1, prod) > 0, ]
```


Select non-zero enhancers for heatmap

```r
omp.pos.pc1.nz <- omp.pos.pc1[rownames(omp.pos.pc1) %in% rownames(mk4.feat.nz), 
    ]
ott3.pos.omp.pc1.nz <- ott3.pos.omp.pc1[rownames(ott3.pos.omp.pc1) %in% rownames(mk4.feat.nz), 
    ]
```



```r
MP.heat(omp.pos.pc1.nz, average = 50, range = c(0, 1.5))
```

![plot of chunk phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb_omp_hmc_omp_pc1](figure/phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb_omp_hmc_omp_pc1.png) 



```r
MP.heat(ott3.pos.omp.pc1.nz, average = 50, range = c(0, 1.5))
```

![plot of chunk phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb_ott3_hmc_omp_pc1](figure/phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb_ott3_hmc_omp_pc1.png) 


Order mean values by OMP PC1

```r
mk4.feat.omp.pc1 <- mk4.feat[match(rownames(omp.pos.pc1), rownames(mk4.feat)), 
    ]
mk4.feat.omp.pc1 <- as.data.frame(mk4.feat.omp.pc1)
mk4.feat.omp.pc1$hmc.ott3.omp <- with(mk4.feat.omp.pc1, computeScoreRatios(ott3_1_hmc_rpkm, 
    omp_hmc_120424_rpkm))
mk4.feat.omp.pc1.c100 <- foreach(c = isplitRows(mk4.feat.omp.pc1[, c(1, 2, 7)], 
    chunks = 100), .combine = "rbind") %do% apply(c, 2, mean)
mk4.feat.omp.pc1.c100 <- as.data.frame(mk4.feat.omp.pc1.c100)
mk4.feat.omp.pc1.c100$index <- 100:1

mk4.feat.omp.pc1.c100.boot <- foreach(c = isplitRows(mk4.feat.omp.pc1[, c(1, 
    2, 7)], chunks = 100), .combine = "rbind") %do% apply(c, 2, bootCI)
mk4.feat.omp.pc1.c100 <- cbind(mk4.feat.omp.pc1.c100, mk4.feat.omp.pc1.c100.boot[seq(1, 
    nrow(mk4.feat.omp.pc1.c100.boot), 2), ], mk4.feat.omp.pc1.c100.boot[seq(2, 
    nrow(mk4.feat.omp.pc1.c100.boot), 2), ])
colnames(mk4.feat.omp.pc1.c100)[5:10] <- c("omp.lower", "ott3.lower", "ott3.omp.lower", 
    "omp.upper", "ott3.upper", "ott3.omp.upper")
```



```r
suppressWarnings(mk4.feat.omp.pc1.c100$wilcox.FDR <- p.adjust(foreach(c = isplitRows(mk4.feat.omp.pc1[, 
    c(1, 2, 7)], chunks = 100), .combine = "rbind") %do% wilcox.test(c[, 3])$p.value, 
    method = "fdr"))
mk4.feat.omp.pc1.c100$wilcox.FDR.05 <- cut(mk4.feat.omp.pc1.c100$wilcox.FDR, 
    breaks = c(0, 0.05, 1))
```



```r
gg <- ggplot(mk4.feat.omp.pc1.c100, aes(hmc.ott3.omp, index))
gg <- gg + geom_vline(xintercept = 0, color = "red")
gg <- gg + geom_errorbarh(aes(xmin = ott3.omp.lower, xmax = ott3.omp.upper), 
    height = 0, size = 0.1) + geom_point(aes(color = wilcox.FDR.05), size = 2) + 
    xlab(bquote(.(~sqrt(bar(RPM))))) + ylab("") + theme(legend.position = "none", 
    axis.text.y = element_blank()) + labs(title = c("O/Tet3-OMP ratio 5hmC by OMP PC1")) + 
    scale_color_manual(values = c("red", "black"))
gg
```

```
## Warning: Removed 16 rows containing missing values (geom_point).
```

![plot of chunk phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb_omp_ott3_hmc_ratio_ord_omp_pc1](figure/phastCons30way_intergenic_sorted_merge500_thresh500_inter_omp_h3k4me1_gc_sub_refgene_extend5kb_omp_ott3_hmc_ratio_ord_omp_pc1.png) 



```r
mk4.feat <- as.data.frame(mk4.feat)
m <- match(rownames(mk4.feat), rna.1log2.rg$enhancer.id)
mk4.feat <- transform(mk4.feat, hmc.ott3.omp = computeScoreRatios(ott3_1_hmc_rpkm, 
    omp_hmc_120424_rpkm), rna.omp = rna.1log2.rg[m, 2], rna.ott3 = rna.1log2.rg[m, 
    3], rna.ott3.omp = rna.1log2.rg[m, 4])
```

```
## Warning: some row.names duplicated:
## 165,175,186,190,204,389,396,494,521,630,672,712,798,809,814,832,947,984,1020,1033,1072,1133,1268,1357,1517,1520,1533,1653,1659,1662,1697,1701,1868,1876,1945,1949,2149,2200,2224,2415,2419,2422,2470,2479,2484,2536,2660,2754,2761,2876,2950,3030,3158,3419,3424,3440,3453,3467
## --> row.names NOT used
```

```r
mk4.feat.n <- na.omit(mk4.feat)
```



```r
with(mk4.feat.n, cor.test(hmc.ott3.omp, rna.ott3.omp))
```

```
## 
## 	Pearson's product-moment correlation
## 
## data:  hmc.ott3.omp and rna.ott3.omp 
## t = 1.623, df = 1972, p-value = 0.1047
## alternative hypothesis: true correlation is not equal to 0 
## 95 percent confidence interval:
##  -0.00760  0.08052 
## sample estimates:
##     cor 
## 0.03653
```


