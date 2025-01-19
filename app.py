from flask import Flask, request, render_template
import os
from datetime import timedelta
from wrapped import load_config, load_cache, save_cache, get_movies_from_2024_sorted_by_rating, get_favorite_movies_by_genre

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        config = load_config()
        cache_file = config['cache_file']
        cache = load_cache(cache_file)
        movies_2024_sorted, total_runtime_minutes, actors_counter, directors_counter, genres_set, most_watched_week, most_watched_day = get_movies_from_2024_sorted_by_rating(file_path, cache)
        save_cache(cache, cache_file)

        # Convert genres_set to a dictionary mapping genres to movies
        genres_dict = {}
        for movie in movies_2024_sorted:
            title, rating, genre, runtime_minutes, year = movie
            if genre not in genres_dict or rating > genres_dict[genre][1]:
                genres_dict[genre] = (title, rating)

        # Prepare top 5 and least 5 movies
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
        movies_2024_sorted_asc = sorted(movies_2024_sorted, key=lambda x: x[1])
        for movie in movies_2024_sorted_asc:
            if len(least_5_movies) < 5 and movie[1] > 0 and movie[0] not in seen_least_5:
                least_5_movies.append(movie)
                seen_least_5.add(movie[0])

        # Format the response
        response = []

        response.append("Top 5 movies watched in 2024 sorted by highest rating:")
        for movie in top_5_movies:
            response.append(f"{movie[0]}: {movie[1]}")

        response.append("\nLeast favorite 5 movies watched in 2024 sorted by lowest rating:")
        for movie in least_5_movies:
            response.append(f"{movie[0]}: {movie[1]}")

        response.append("\nTop 5 movies made in 2024 sorted by highest rating:")
        for movie in top_5_movies_made_in_2024:
            response.append(f"{movie[0]}: {movie[1]}")

        favorite_movies_by_genre = get_favorite_movies_by_genre(movies_2024_sorted)
        response.append("\nFavorite movies by genres in 2024:")
        for genre in genres_set:
            if genre in favorite_movies_by_genre:
                movie, rating = favorite_movies_by_genre[genre]
                response.append(f"{genre}: {movie} ({rating})")
            else:
                response.append(f"{genre}: No movies found")

        response.append("\nTop 5 actors in 2024:")
        for actor, count in actors_counter.most_common(5):
            response.append(f"{actor}: {count} movies")

        response.append("\nTop 5 directors in 2024:")
        top_5_directors = directors_counter.most_common(6)  # Get top 6 to account for possible "N/A"
        count = 0
        for director, count in top_5_directors:
            if director != "N/A":
                response.append(f"{director}: {count} movies")
                count += 1
            if count == 5:
                break

        if most_watched_week:
            week_start, count = most_watched_week
            week_end = week_start + timedelta(days=6)
            response.append(f"\nWeek with most watched movies: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')} with {count} movies")
        else:
            response.append("\nWeek with most watched movies: No data")

        if most_watched_day:
            response.append(f"\nDay of the week with most movies watched: {most_watched_day[0]} with {most_watched_day[1]} movies")
        else:
            response.append("\nDay of the week with most movies watched: No data")

        response.append(f"\nTotal runtime of movies watched in 2024: {total_runtime_minutes} minutes")

        # Debug print to check the response content
        print('\n'.join(response))

        return '\n'.join(response), 200

if __name__ == '__main__':
    app.run(debug=True)