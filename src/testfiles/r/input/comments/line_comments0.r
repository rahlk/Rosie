# Read file
statesInfo <- read.csv('stateData.csv')
# subset data by region if region is 1
subset(statesInfo, state.region == 1)
stateSubset <- statesInfo[statesInfo$illiteracy == 0.5, ]

# Attributes and dimensions of data
dim(stateSubset)
str(stateSubset)

stateSubset # print out stateSubset
