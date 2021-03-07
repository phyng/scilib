#!/usr/bin/env Rscript

library(gender)

args = commandArgs(trailingOnly=TRUE)

if (length(args)==0) {
  stop("At least one argument must be supplied", call.=FALSE)
}

names = unlist(strsplit(args[2], ","))
results = gender(names, method = "ssa")
for (index in rownames(results)) {
    write(paste(toString(results[index, "name"]), toString(results[index, "gender"]), sep=","), stdout())
}
