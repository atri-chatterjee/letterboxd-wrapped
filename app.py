from flask import Flask, request, render_template
import os
from datetime import timedelta
from wrapped import load_config, load_cache, save_cache, get_movies_from_2024_sorted_by_rating

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

        # Format the response
        response = []

        response.append("Top 5 movies watched in 2024 sorted by highest rating:")
        for movie in movies_2024_sorted[:5]:
            response.append(f"{movie[0]}: {movie[1]}")

        response.append("\nLeast favorite 5 movies watched in 2024 sorted by lowest rating:")
        for movie in movies_2024_sorted[-5:]:
            response.append(f"{movie[0]}: {movie[1]}")

        response.append("\nTop 5 movies made in 2024 sorted by highest rating:")
        for movie in [m for m in movies_2024_sorted if m[4] == 2024][:5]:
            response.append(f"{movie[0]}: {movie[1]}")

        response.append("\nFavorite movies by genres in 2024:")
        for genre, movie in genres_dict.items():
            response.append(f"{genre}: {movie[0]} ({movie[1]})")

        response.append("\nTop 5 actors in 2024:")
        for actor, count in actors_counter.most_common(5):
            response.append(f"{actor}: {count} movies")

        response.append("\nTop 5 directors in 2024:")
        for director, count in directors_counter.most_common(5):
            response.append(f"{director}: {count} movies")

        if most_watched_week:
            response.append(f"\nWeek with most watched movies: {most_watched_week[0]} to {most_watched_week[0] + timedelta(days=6)} with {most_watched_week[1]} movies")
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