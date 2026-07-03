from uuid import UUID

from question_agent.states.chunk_hit import ChunkHit


class RRFService:

    def fuse_rankings(self, ranked_lists: list[list[ChunkHit]], k: int, top_n: int, weights: list[float]) -> list[ChunkHit]:

        rrf_scores: dict[UUID, float] = {}                                                              # contains the chunk_id : rrf score
        seen_hits: dict[UUID, ChunkHit] = {}                                                            # stores all the unique chunks from all lists


        for retriever_index in range(len(ranked_lists)):                                                # retriever index to loop over the different ranked lists
            ranked_hits = ranked_lists[retriever_index]
            weight = weights[retriever_index]
            for rank, hit in enumerate(ranked_hits, start=1):
                contribution = weight / (k + rank)
                rrf_scores[hit.chunk_id] = rrf_scores.get(hit.chunk_id, 0.0) + contribution
                if hit.chunk_id not in seen_hits:
                    seen_hits[hit.chunk_id] = hit

        top_chunk_ids = sorted(                                                                         # only stores the chunk_id after RRF
            rrf_scores,                                                                                 # Lambda function => lambda <input> : <return/working>
            key=lambda chunk_id: rrf_scores[chunk_id],                                                  # Lambda function , key is used to assign on which value we have to sort
            reverse=True,                                                                               # sort in descending
        )[:top_n]

        fused: list[ChunkHit] = []
        for chunk_id in top_chunk_ids:
            original = seen_hits[chunk_id]
            fused.append(
                ChunkHit(
                    chunk_id=original.chunk_id,
                    doc_id=original.doc_id,
                    content=original.content,
                    score=rrf_scores[chunk_id],
                )
            )
        return fused
