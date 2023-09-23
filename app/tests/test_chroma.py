from core import get_similar_docs


class TestChroma:

    def test_chroma_query_filter_and(self):
        docs = get_similar_docs(
            "카카오 싱크가 뭐야",
            filters={"$and": [{"data_source": "sync"}, {"category": "Title"}]},
            only_contents=False,
            top_k=50
        )
        for doc in docs:
            assert doc.metadata["category"] == "Title"
            assert doc.metadata["data_source"] == "sync"
            print(doc)

    def test_chroma_query_filter_not_in(self):
        docs = get_similar_docs(
            "카카오 싱크가 뭐야",
            filters={"$and": [
                {"data_source": "sync"},
                {"category": {"$ne": "Title"}}
            ]},
            only_contents=False,
            top_k=50
        )
        for doc in docs:
            print(doc)

    def test_chroma_query_filter_equal(self):
        docs = get_similar_docs(
            "카카오톡 채널을 추가하려면 어떻게 해?",
            filters={
                "$and": [
                    {"data_source": "channel"},
                    {"category": {"$eq": "NarrativeText"}}
                ]
            },
            only_contents=False,
            top_k=50
        )
        for doc in docs:
            print(doc)

    def test_chroma_query(self):
        docs = get_similar_docs(
            "카카오톡 채널을 추가하려면 어떻게 해?",
            filters={"data_source": "channel"},
            only_contents=False,
            top_k=50
        )
        for doc in docs:
            print(doc)
