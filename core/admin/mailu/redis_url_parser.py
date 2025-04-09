from urllib.parse import urlparse

def parse_redis_url(url):
    """
    Parse a Redis URL into its components.
    
    Expected formats:
      - redis://[{username}:{password}@]host[:port]/db
      - rediss://[{username}:{password}@]host[:port]/db (indicates TLS)
    
    The function returns a dictionary with the following keys:
      - username: Optional username (or None)
      - password: Optional password (or None)
      - host: The Redis server hostname or IP address
      - port: The port number (default is 6379 for non-TLS and 6380 for TLS if not specified)
      - db: The database index as an integer (default 0 if not specified)
      - use_tls: Boolean flag, True if the URL scheme is "rediss", False otherwise.
      
    Raises:
      ValueError: If the URL scheme is not valid, if the host is missing,
                  or if the DB portion is not a valid integer.
    """
    parsed = urlparse(url)
    
    # Validate the scheme: must be either 'redis' or 'rediss'
    if parsed.scheme not in ("redis", "rediss"):
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}. Use 'redis://' or 'rediss://'.")
    use_tls = parsed.scheme == "rediss"
    
    # Ensure the host is present
    if not parsed.hostname:
        raise ValueError("Invalid URL: Host is missing.")

    host = parsed.hostname
    
    # Determine the port: default port is 6379 for non-TLS, or 6380 for TLS if not provided.
    port = parsed.port if parsed.port else (6380 if use_tls else 6379)
    
    # Username and password are optional
    username = parsed.username
    password = parsed.password
    
    # Parse the database number from the path.
    # The path should be of the form '/0' for DB index 0. Remove the leading '/'
    if parsed.path and len(parsed.path) > 1:
        try:
            db = int(parsed.path.lstrip("/"))
        except ValueError:
            raise ValueError(f"Invalid database number in URL path: '{parsed.path}'.")
    else:
        db = 0  # Default DB index
    
    return {
        "username": username,
        "password": password,
        "host": host,
        "port": port,
        "db": db,
        "use_tls": use_tls,
    }

# Testing on some sample URLs
if __name__ == "__main__":
    test_urls = [
        "redis://localhost/0",
        "redis://:secret@redis.example.com/2",
        "redis://user:secret@redis.example.com:6380/1",
        "rediss://user:secret@secure.redis.com/3",
        # Edge case: missing DB portion defaults to 0.
        "redis://redis.example.com",
    ]

    for url in test_urls:
        try:
            result = parse_redis_url(url)
            print(f"Parsed URL: {url}")
            print(result)
            print("-" * 40)
        except ValueError as error:
            print(f"Error parsing '{url}': {error}")
