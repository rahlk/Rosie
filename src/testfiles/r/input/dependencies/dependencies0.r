# Read file
statesInfo <- read.csv('stateData.csv')
# subset data by region if region is 1
subset(statesInfo, state.region == 1)
stateSubset <- statesInfo[statesInfo$illiteracy == 0.5, ]

library(ggplot2)
library(plyr)

library(twitteR)

# Attributes and dimensions of data
dim(stateSubset)
str(stateSubset)

source(file.path(codeDir, 'dependencies.r'))

stateSubset # print out stateSubset
