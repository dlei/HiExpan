### Start ElasticSearch with 16GB memory

```
$ ES_JAVA_OPTS="-Xms16g -Xmx16g" ./bin/elasticsearch
```

#### Source filter search

```
curl -XGET 'localhost:9200/wiki/eid2skipgram/_search?pretty' -H 'Content-Type: application/json' -d'
{
  "_source": false,
  "query": {
    "match": {
      "skipgrams": "sg1087842 sg508794"
    }
  }
}'
```