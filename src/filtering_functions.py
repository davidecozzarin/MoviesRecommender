def filter_movies(dataset, title=None, genre=None, min_duration=None, max_duration=None, actors=None, directors=None, start_year=None, end_year=None):

    filtered = dataset.copy()

    if title:
        filtered = filtered[filtered['title'].str.contains(title, case=False, na=False)]

    if genre:
        filtered = filtered[filtered['genre'].apply(lambda x: any(g in x for g in genre))]

    if min_duration is not None:
        filtered = filtered[filtered['duration'] >= min_duration]
    if max_duration is not None:
        filtered = filtered[filtered['duration'] <= max_duration]

    if actors:
        actor_list = [a.strip() for a in actors.split(",")]
        filtered = filtered[filtered['actors'].apply(lambda x: any(actor in x for actor in actor_list))]

    if directors:
        director_list = [d.strip() for d in directors.split(",")]
        filtered = filtered[filtered['directors'].apply(lambda x: any(director in x for director in director_list))]

    if start_year is not None:
        filtered = filtered[filtered['year'] >= start_year]
    if end_year is not None:
        filtered = filtered[filtered['year'] <= end_year]

    return filtered

def search_movie(dataset, title=None):
    filtered = dataset.copy()
    if title:
        filtered = filtered[filtered['title'].str.contains(title, case=False, na=False)]
    return filtered