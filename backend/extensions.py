from flask_caching import Cache

# Initialize the cache without the app object.
# It will be bound to the app in app.py.
cache = Cache()
