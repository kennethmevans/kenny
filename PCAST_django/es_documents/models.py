from elasticsearch_dsl import Document, Text, Keyword

from elasticsearch_dsl import Document, Text, Keyword

class ESDocument(Document):
    title = Text()
    asset_id = Keyword()
    full_text = Text(fields={
        "ngram": Text(analyzer="edge_ngram_analyzer")
    })

    class Index:
        name = 'documents'
