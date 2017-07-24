statesInfo <- read.csv('stateData.csv')

subset(statesInfo, state.region == 1)
stateSubset <- statesInfo[statesInfo$illiteracy == 0.5, ]


dim(stateSubset)
str(stateSubset)

stateSubset
