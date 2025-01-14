def filter_movies(dataset, title=None, genre=None, min_duration=None, max_duration=None, actors=None, directors=None, start_year=None, end_year=None):
    """
    Filters the movies dataset based on user inputs.
    
    Parameters:
        dataset (DataFrame): The dataset of movies.
        title (str): Filter movies by title (partial or full match).
        genre (list): Filter movies by a list of genres.
        min_duration (int): Minimum duration of movies.
        max_duration (int): Maximum duration of movies.
        actors (str): Filter movies by actor name (comma-separated list).
        directors (str): Filter movies by director name (comma-separated list).
        start_year (int): Start year for filtering movies (inclusive).
        end_year (int): End year for filtering movies (inclusive).
    
    Returns:
        DataFrame: Filtered dataset based on the given parameters.
    """
    filtered = dataset.copy()

    # Filter by title
    if title:
        filtered = filtered[filtered['title'].str.contains(title, case=False, na=False)]

    # Filter by genre
    if genre:
        filtered = filtered[filtered['genre'].apply(lambda x: any(g in x for g in genre))]

    # Filter by duration
    if min_duration is not None:
        filtered = filtered[filtered['duration'] >= min_duration]
    if max_duration is not None:
        filtered = filtered[filtered['duration'] <= max_duration]

    # Filter by actors
    if actors:
        actor_list = [a.strip() for a in actors.split(",")]
        filtered = filtered[filtered['actors'].apply(lambda x: any(actor in x for actor in actor_list))]

    # Filter by directors
    if directors:
        director_list = [d.strip() for d in directors.split(",")]
        filtered = filtered[filtered['directors'].apply(lambda x: any(director in x for director in director_list))]

    # Filter by year
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