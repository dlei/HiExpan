### owner: Ellen Wu, Jiaming Shen, Dongming Lei

This folder contains scripts to generate input files for FTS model (KDD trial). To run, simply change the corpus (data) name in dataProcess.sh and run ./dataProcess.sh

You may need to provide a raw json source file: "../../data/{corpus name}/source/sentences.json.raw". You can find the example json file in dm4 server: "/shared/data/zeqiuwu1/fts-summer/data/wiki/source/sentences.json.raw"


### TODO

1. Later we can try to use raw word2vec embedding tools, which may give better performance compared with PTE
2. obtainEntityAndTypeList.py里面对于一个entity mentions有多个types的处理似乎有点问题，check it later


