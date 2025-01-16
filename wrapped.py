import csv
import requests
import json
from datetime import datetime
from collections import defaultdict, Counter
from secrets import OMDB_API_KEY  # Import the API key from secrets.py

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def load_cache(cache_file):
    try:
        with open(cache_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_cache(cache, cache_file):
    with open(cache_file, 'w') as f:
        json.dump(cache, f)

def get_movie_details(title, cache):
    if title in cache and all(key in cache[title] for key in ['genres', 'runtime', 'year', 'actors', 'director']):
        return cache[title]['genres'], cache[title]['runtime'], cache[title]['year'], cache[title]['actors'], cache[title]['director']
    
    url = f"https://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('Error') == 'Request limit reached!':
            raise Exception('API request limit reached!')
        if 'Genre' in data and 'Runtime' in data and 'Year' in data and 'Actors' in data and 'Director' in data:
            genres = data['Genre'].split(', ')
            runtime = data['Runtime']
            year = data['Year']
            actors = [actor for actor in data['Actors'].split(', ') if actor != "N/A"]
            director = data['Director'] if data['Director'] != "N/A" else None
            cache[title] = {'genres': genres, 'runtime': runtime, 'year': year, 'actors': actors, 'director': director}
            return genres, runtime, year, actors, director
        else:
            raise Exception(f"Details not found for {title}")
    elif response.status_code == 401:
        raise Exception('Unauthorized: Invalid API key')
    else:
        raise Exception(f"Failed to retrieve details for {title}: {response.status_code}")

def get_movies_from_2024_sorted_by_rating(csv_file_path, cache):
    movies = []
    total_runtime_minutes = 0
    seen_movies = set()
    actors_counter = Counter()
    directors_counter = Counter()
    genres_set = set()
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row and len(row) > 0:
                try:
                    date = datetime.strptime(row[0], '%Y-%m-%d')
                    if date.year == 2024:
                        rating = float(row[4]) if row[4] else 0
                        title = row[1]
                        if title in seen_movies:
                            continue
                        seen_movies.add(title)
                        genres, runtime, year, actors, director = get_movie_details(title, cache)
                        if genres and runtime:
                            runtime_minutes = int(runtime.split(' ')[0]) if runtime != "N/A" else 0
                            total_runtime_minutes += runtime_minutes
                            for genre in genres:
                                movies.append((title, rating, genre, runtime_minutes, year))  # (movie title, rating, genre, runtime_minutes, year)
                                genres_set.add(genre)
                            actors_counter.update(actors)
                            if director:
                                directors_counter.update([director])
                except ValueError:
                    continue
                except Exception as e:
                    print(f"Error: {e}")
                    break
    # Sort movies by rating in descending order
    movies.sort(key=lambda x: x[1], reverse=True)
    return movies, total_runtime_minutes, actors_counter, directors_counter, genres_set

def get_favorite_movies_by_genre(movies):
    genre_dict = defaultdict(list)
    for movie, rating, genre, _, _ in movies:
        genre_dict[genre].append((movie, rating))
    
    favorite_movies_by_genre = {}
    for genre, movies in genre_dict.items():
        movies.sort(key=lambda x: x[1], reverse=True)
        favorite_movies_by_genre[genre] = movies[0]  # Get the highest rated movie in each genre
    
    return favorite_movies_by_genre

if __name__ == "__main__":
    config = load_config()
    cache_file = config['cache_file']
    csv_file_path = config['csv_file_path']
    
    cache = load_cache(cache_file)
    movies_2024_sorted, total_runtime_minutes, actors_counter, directors_counter, genres_set = get_movies_from_2024_sorted_by_rating(csv_file_path, cache)
    save_cache(cache, cache_file)
    
    top_5_movies = []
    least_5_movies = []
    top_5_movies_made_in_2024 = []
    seen_top_5 = set()
    seen_least_5 = set()
    seen_top_5_made_in_2024 = set()
    
    for movie in movies_2024_sorted:
        if len(top_5_movies) < 5 and movie[0] not in seen_top_5:
            top_5_movies.append(movie)
            seen_top_5.add(movie[0])
        if len(top_5_movies_made_in_2024) < 5 and movie[4] == '2024' and movie[0] not in seen_top_5_made_in_2024:
            top_5_movies_made_in_2024.append(movie)
            seen_top_5_made_in_2024.add(movie[0])
    
    # Sort movies by rating in ascending order for least favorite movies
    movies_2024_sorted.sort(key=lambda x: x[1])
    for movie in movies_2024_sorted:
        if len(least_5_movies) < 5 and movie[1] > 0 and movie[0] not in seen_least_5:
            least_5_movies.append(movie)
            seen_least_5.add(movie[0])
    
    print("Top 5 movies watched in 2024 sorted by highest rating:")
    for movie, rating, _, _, _ in top_5_movies:
        print(f"{movie}: {rating}")
    
    print("\nLeast favorite 5 movies watched in 2024 sorted by lowest rating:")
    for movie, rating, _, _, _ in least_5_movies:
        print(f"{movie}: {rating}")
    
    print("\nTop 5 movies made in 2024 sorted by highest rating:")
    for movie, rating, _, _, _ in top_5_movies_made_in_2024:
        print(f"{movie}: {rating}")
    
    favorite_movies_by_genre = get_favorite_movies_by_genre(movies_2024_sorted)
    print("\nFavorite movies by genres in 2024:")
    for genre in genres_set:
        if genre in favorite_movies_by_genre:
            movie, rating = favorite_movies_by_genre[genre]
            print(f"{genre}: {movie} ({rating})")
        else:
            print(f"{genre}: No movies found")
    
    top_5_actors = actors_counter.most_common(5)
    top_5_directors = directors_counter.most_common(6)  
    
    print("\nTop 5 actors in 2024:")
    for actor, count in top_5_actors:
        print(f"{actor}: {count} movies")
    
    print("\nTop 5 directors in 2024:")
    count = 0
    for director, count in top_5_directors:
        if director != "N/A":
            print(f"{director}: {count} movies")
            count += 1
        if count == 5:
            break
    
    print(f"\nTotal runtime of movies watched in 2024: {total_runtime_minutes} minutes")