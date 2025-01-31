from flask import Flask, request, render_template
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import requests
import groq
app = Flask(__name__)
api_url = "Groq_api_key"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    video_url = request.form['video_url']

    try:
        # Extract video ID from URL
        parsed_url = urlparse(video_url)
        if parsed_url.hostname == 'youtu.be':
            video_id = parsed_url.path[1:]  # Shortened URL format
        elif parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get('v', [None])[0]
        else:
            return "Invalid YouTube URL", 400

        if not video_id:
            return "Video ID could not be extracted. Please check your URL.", 400

        # Fetch the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry['text'] for entry in transcript])

        return render_template('query.html', transcript=transcript_text)
    except Exception as e:
        return f"Error fetching transcript: {e}", 400

@app.route('/process_query', methods=['POST'])
def process_query():
    transcript = request.form['transcript']
    query = request.form['query']

    try:
        # Send transcript and query to Groq API
        response = requests.post(api_url, json={"transcript": transcript, "query": query})

        if response.status_code == 200:
            api_response = response.json()
            return render_template('result.html', query=query, response=api_response['result'])
        else:
            return f"Error from Groq API: {response.status_code}", 400
    except Exception as e:
        return f"Error processing query: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
