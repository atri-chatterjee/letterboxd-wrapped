import csv
import requests
import json
from datetime import datetime
from collections import defaultdict
from secrets import OMDB_API_KEY  # Import the API key from secrets.py

CACHE_FILE = 'movie_cache.json'

def load_cache():
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def get_movie_details(title, cache):
    if title in cache:
        return cache[title]['genres'], cache[title]['runtime'], cache[title]['year']
    
    url = f"https://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('Error') == 'Request limit reached!':
            raise Exception('API request limit reached!')
        if 'Genre' in data and 'Runtime' in data and 'Year' in data:
            genres = data['Genre'].split(', ')
            runtime = data['Runtime']
            year = data['Year']
            cache[title] = {'genres': genres, 'runtime': runtime, 'year': year}
            return genres, runtime, year
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
                        genres, runtime, year = get_movie_details(title, cache)
                        if genres and runtime:
                            runtime_minutes = int(runtime.split(' ')[0]) if runtime != "N/A" else 0
                            total_runtime_minutes += runtime_minutes
                            for genre in genres:
                                movies.append((title, rating, genre, runtime_minutes, year))  # (movie title, rating, genre, runtime_minutes, year)
                except ValueError:
                    continue
                except Exception as e:
                    print(f"Error: {e}")
                    break
    # Sort movies by rating in descending order
    movies.sort(key=lambda x: x[1], reverse=True)
    return movies, total_runtime_minutes

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
    cache = load_cache()
    csv_file_path = '/Users/atrichatterjee/src/letterboxd-wrapped/diary.csv'
    movies_2024_sorted, total_runtime_minutes = get_movies_from_2024_sorted_by_rating(csv_file_path, cache)
    save_cache(cache)
    
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
    specified_genres = ["Action", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi", "Sports"]
    print("\nFavorite movies by specified genres in 2024:")
    for genre in specified_genres:
        if genre in favorite_movies_by_genre:
            movie, rating = favorite_movies_by_genre[genre]
            print(f"{genre}: {movie} ({rating})")
        else:
            print(f"{genre}: No movies found")
    
    print(f"\nTotal runtime of movies watched in 2024: {total_runtime_minutes} minutes")