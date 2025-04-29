from django.apps import AppConfig
from django.conf import settings
from elasticsearch_dsl import connections
from elasticsearch import Elasticsearch

class ESDocumentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'es_documents'

    def ready(self):
        # Create connection using settings
        connections.create_connection(alias='default', **settings.ELASTICSEARCH_DSL['default'])

        from elasticsearch import Elasticsearch
        client: Elasticsearch = connections.get_connection()

        # Check if index already exists
        if not client.indices.exists(index="documents"):
            print("🔧 'documents' index not found. Creating with edge_ngram analyzer...")

            # Create index with edge_ngram analyzer and mapping
            client.indices.create(
                index="documents",
                body={
                    "settings": {
                        "analysis": {
                            "tokenizer": {
                                "edge_ngram_tokenizer": {
                                    "type": "edge_ngram",
                                    "min_gram": 2,
                                    "max_gram": 20,
                                    "token_chars": ["letter", "digit"]
                                }
                            },
                            "analyzer": {
                                "edge_ngram_analyzer": {
                                    "type": "custom",
                                    "tokenizer": "edge_ngram_tokenizer"
                                }
                            }
                        }
                    },
                    "mappings": {
                        "properties": {
                            "title": {"type": "text"},
                            "asset_id": {"type": "keyword"},
                            "full_text": {
                                "type": "text",
                                "fields": {
                                    "ngram": {
                                        "type": "text",
                                        "analyzer": "edge_ngram_analyzer"




                                    }
                                }
                            }
                        }
                    }
                }
            )
            print("✅ 'documents' index created.")
        else:
            print("✅ 'documents' index already exists.")


