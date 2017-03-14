## TextAI
REST API for Text Summarization and Keywords Extraction from a given URL

Project has to major pieces:

1. REST API built on top of Python's Klein/Twisted server framework
2. Frontend written in pure jQuery which uses HN realtime feed to generate
summaries with help of REST endpoint

Everything has been wrapped into Docker container (See Dockerfile) and can be run using simple 
Docker cli tool:

```
git clone https://github.com/bexp/textai.git && cd textai
docker build -t bexpace/hntop .
docker run -d -p 8000:8080 --restart on-failure --ulimit nofile=4096:4096 bexpace/hntop
```

View in action at http://hn10.org
