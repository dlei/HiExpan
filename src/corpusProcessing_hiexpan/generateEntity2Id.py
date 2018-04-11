import json
import sys

def main():
    corpusName = sys.argv[1]
    sentence_json_path = "../../data/"+corpusName+"/intermediate/sentences.json.spacy"
    output_json = "../../data/"+corpusName+"/intermediate/sentences.json"
    output_entity2id_path = "../../data/"+corpusName+"/intermediate/entity2id.txt"
    with open(sentence_json_path) as fin, open(output_json, 'w') as fout:
        entity2id = {}
        for line in fin:
            line = line.strip()
            
            try:
                data = json.loads(line)
                for i,ent in enumerate(data["entityMentions"]):
                    entName = ent["text"]
                    if entName not in entity2id:
                        entity2id[entName] = len(entity2id)

                    entId = entity2id[entName]
                    data["entityMentions"][i]["entityId"] = entId
                
                json.dump(data, fout)
                fout.write("\n")
            except:
                print(line)
                continue

    with open(output_entity2id_path, "w") as fout:
        for k,v in entity2id.items():
            fout.write(k+"\t"+str(v)+"\n")


main()
