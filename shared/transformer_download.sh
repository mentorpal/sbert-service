#!/bin/sh
transformer_path=installed/sentence-transformer
OUTFILE="${transformer_path}/distilbert-base-nli-mean-tokens.zip"

if [[ -e ${transformer_path} ]]
then
    echo "Transformer already downloaded"
    exit 0
fi
mkdir -p ${transformer_path}
curl https://public.ukp.informatik.tu-darmstadt.de/reimers/sentence-transformers/v0.2/distilbert-base-nli-mean-tokens.zip  --output $OUTFILE
(cd $transformer_path && unzip -x *.zip && rm *.zip)
