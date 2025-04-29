from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from elasticsearch_dsl.connections import get_connection
from elasticsearch import NotFoundError
from .models import ESDocument


class ESDocumentViewSet(ViewSet):
    """
    A ViewSet for creating, listing, deleting index, and fuzzy searching Elasticsearch documents.
    """

    @action(detail=False, methods=['post'])
    def create_document(self, request):
        """
        Save a document to Elasticsearch.
        """
        try:
            data = request.data
            doc = ESDocument(
                title=data.get("title", ""),
                asset_id=data.get("asset_id", ""),
                full_text=data.get("full_text", ""),
            )
            doc.save()
            return Response({"message": "Document saved successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def list_documents(self, request):
        """
        Return all documents from the Elasticsearch index.
        """
        results = ESDocument.search().execute()
        data = [
            {
                "title": hit.title,
                "asset_id": hit.asset_id,
                "full_text": hit.full_text,
            }
            for hit in results
        ]
        return Response({"results": data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Fuzzy substring search using full_text.ngram field.
        """
        query = request.query_params.get("q", "")
        if not query:
            return Response({"error": "Missing 'q' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Use match query on ngram subfield
            results = ESDocument.search().query("match", **{"full_text.ngram": query}).execute()
            data = [
                {
                    "title": hit.title,
                    "asset_id": hit.asset_id,
                    "full_text": hit.full_text,
                }
                for hit in results
            ]
            return Response({"results": data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['delete'])
    def delete_index(self, request):
        """
        Delete the 'documents' index from Elasticsearch.
        Useful for resetting before re-creating with custom analyzer.
        """
        client = get_connection()
        try:
            client.indices.delete(index='documents')
            return Response({"message": "Index 'documents' deleted."}, status=status.HTTP_200_OK)
        except NotFoundError:
            return Response({"message": "Index 'documents' does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
