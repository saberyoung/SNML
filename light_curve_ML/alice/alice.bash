if [ $USER = 'enrico' ]; then
    alice_dir="$HOME/ownCloud/scripts/alice/"
elif [ $USER = 'hal' ]; then
    alice_dir="/dark/hal/test_sheng/code_sheng/machine-learning/snML/light_curve_ML/alice/"
else
    alice_dir="/home/enrico/ownCloud/scripts/alice/"
fi

export alice_dir

#if [ -z "$hlib" ]; then
#  echo "!!! Error: you need to initialize scisoft !!!"
#   return
#fi

#  alice
alias alice="python ${alice_dir}alice.py"
alias snlc="python ${alice_dir}snlc.py"
alias am="python ${alice_dir}am.py"
alias col="python ${alice_dir}col.py"
alias lsf="python ${alice_dir}lsf.py"
alias verify="python ${alice_dir}verify.py"
alias alicelist="python ${alice_dir}alicelist.py"
alias bolom="python ${alice_dir}bolom.py"

alice
