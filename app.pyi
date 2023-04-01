from flask import Flask

app: Flask

@app.route('/')
def home(): ...
@app.route('/api/auth')
def auth_root(): ...
@app.route('/api/auth/callback')
def auth_callback(): ...
@app.route('/api/me')
def me(): ...
@app.route('/api/recommendations', methods=['GET', 'POST'])
def api_recommendations(): ...
@app.route('/api/recommendations/{id}', methods=['PATCH', 'DELETE'])
def api_recommendation(id: str): ...
@app.route('/api/recommendations/{id}/votes', methods=['POST'])
def api_recommendation_votes(id: str): ...
