EMBEDDING_METHOD=word2vec
data=$1
path=$(pwd)
if [ "$EMBEDDING_METHOD" == "PTE" ]; then
	echo 'generating embedding files using PTE'
	python3 prepareFormatForEmbed.py $data
	cd ../tools/PTE/
	make
	chmod +x ./run.sh
	./run.sh $data
	cd $path
	python3 getEmbFile.py $data PTE
elif [ "$EMBEDDING_METHOD" == "word2vec" ]; then
	echo 'generating embedding files using word2vec'
	python3 prepareFormatForEmbed_word2vec.py $data
	cd ../tools/word2vec/src
	make
	cd ../
	chmod +x ./run.sh
	./run.sh $data
	cd $path
	python3 getEmbFile.py $data word2vec
fi