statesInfo <- read.csv('stateData.csv')

subset(statesInfo, state.region == 1)
stateSubset <- statesInfo[statesInfo$illiteracy == 0.5, ]

#square <- function(x) {
#    sq <- x * x
#    return(square)
#}
dim(stateSubset)
str(stateSubset)

stateSubset
