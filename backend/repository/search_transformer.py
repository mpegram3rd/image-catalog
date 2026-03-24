# =============================================================================
# search_transformer.py - ChromaDB Search Results Transformer
# =============================================================================

from chromadb import QueryResult

from models.api_models import SearchResult


def transform(results: QueryResult, cutoff_threshold: float) -> list[SearchResult]:
    """
    Transforms a ChromaDB QueryResult into a filtered list of SearchResult objects.

    The transformation process:
        1. Extracts the first result's data as a reference point for distance comparison
        2. Iterates through all results, calculating relative distances from the closest match
        3. Stops processing when results exceed the cutoff threshold (optimization)
        4. Builds SearchResult objects with image_path, description, thumbnail, and distance

    Args:
        results (QueryResult): The raw ChromaDB query result containing ids, metadatas,
                              distances, and documents from the vector search.
        cutoff_threshold (float): The maximum relative distance threshold. Results with
                                  a relative distance >= this value will be excluded.

    Returns:
        list[SearchResult]: A filtered list of SearchResult objects containing only
                           the most relevant matches based on distance thresholding.
    """

    search_results: list[SearchResult] = []

    # Chroma Structure is wonky, so we're going to save some processing
    # by pre-fetching the first result from each category we want to work with
    # for mapping.  This is viable because we only submit 1 search request at a time
    ids = results['ids'][0]
    metadata = results['metadatas'][0]
    distances = results['distances'][0]
    documents = results['documents'][0]

    # The closest distance to our search item.  We're going to use this distance
    # to calculate a threshold by which search results are "too far away" to be worth consideration.
    initial_distance = distances[0]
    # TODO If initial distance is too far (? > 0.5 ?) then maybe return nothing.

    index = 0
    while index < len(ids):

        # Calculate a relative distance from the closest result to determine if we
        # should stop processing results.  The value represents roughly a measure of
        # the distance difference between the closest result and the current as a percentage
        # of the total distance of the closest result to the search item.
        # The key idea is that as results diverge further they're significantly less relevant
        if initial_distance != 0.0:
           relative_distance = abs(distances[index] - initial_distance) / abs(initial_distance)
        else:
            relative_distance = distances[index]

        if relative_distance >= cutoff_threshold:
            break

        if 'description' in metadata[index]:
            description = metadata[index]['description']
        else:
            description = documents[index]

        search_results.append(
            SearchResult(
                image_path=ids[index],
                description=description,
                thumbnail=metadata[index]['thumbnail'],
                distance = distances[index]
            )
        )

        index += 1

    return search_results
