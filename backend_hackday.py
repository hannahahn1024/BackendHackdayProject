import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/repositories', methods=['GET'])
def get_repository_stats():
    #get the GitHub username from the query parameters
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username parameter is mission.'}), 400

    #get the 'forked' query parameter and set the flag accordingly
    forked = request.args.get('forked', default = 'true').lower() == 'true'
    
    try:
        #Fetch user repositories from GitHub API
        repositories_url = f'https://api.github.com/users/{username}/repos'
        response = requests.get(repositories_url)
        response.raise_for_status()
        repositories = response.json()

        #filter repositories based on the 'forked' flag
        if not forked:
            repositories = [repo for repo in repositories if not repo['fork']]

        #calculate aggregated statistics
        total_count = len(repositories)
        total_stargazesrs = sum(repo['stargazers_count'] for repo in repositories)
        total_forks = sum(repo['forks_count'] for repo in repositories)
        total_size = sum(repo['size'] for repo in repositories)
        average_size = total_size / total_count if total_count > 0 else 0

        #count languages
        languages = {}
        for repo in repositories:
            language = repo['language']
            if language:
                languages[language] = languages.get(language, 0) + 1

        #sort languages by count (most used to least used)
        sorted_languages = sorted(languages.items(), key = lambda x: x[1], reverse = True)

        #prepare the response
        response_data = {
            'total_count': total_count,
            'total_stargazers': total_stargazesrs,
            'total_forks': total_forks,
            'average_size': average_size,
            'languages': sorted_languages
        }
        return jsonify(response_data)
    except requests.exceptions.RequestException as e:
        return jsonify({'error':str(e)}), 500
if __name__ == '__main__':
    app.run()