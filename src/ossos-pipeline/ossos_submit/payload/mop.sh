#!/bin/bash
# Run the Moving Object Pipeline on the given exposure numbers
source ${HOME}/.bash_profile

ccd=$4

if [ $# -eq 5 ] ; then 
 force=$5 
fi

## First do the search images
mkpsf.py $1 $2 $3 --ccd $ccd -v  ${force}
step1.py $1 $2 $3 --ccd $ccd -v  ${force}
step2.py $1 $2 $3 --ccd $ccd -v  ${force}
step3.py $1 $2 $3 --ccd $ccd -v  ${force}
echo "Running combine.py"
echo combine.py $1 -v  --ccd $ccd ${force}
combine.py $1 -v  --ccd $ccd ${force}

## Now build a scramble set and search
scramble.py $1 $2 $3 --ccd $ccd -v  ${force}
plant.py $1 $2 $3 --ccd $ccd -v ${force}
step1.py $1 $2 $3 --ccd $ccd --fk --type s -v  ${force}
step2.py $1 $2 $3 --ccd $ccd --fk --type s -v  ${force}
step3.py $1 $2 $3 --ccd $ccd --fk --type s -v ${force}
echo "Running combine.py"
echo combine.py $1 --ccd $ccd --fk --type s -v  ${force}
combine.py $1 --ccd $ccd --fk --type s -v  ${force}
