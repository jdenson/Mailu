from urllib.parse import urlparse, parse_qs

def parse_redis_url(url):
    """
    Parse a Redis URL into its components.
    
    Expected formats:
      - redis://[{username}:{password}@]host[:port]/db
      - rediss://[{username}:{password}@]host[:port]/db (indicates TLS)
      - redis+unix:///path/to/socket
    
    The function returns a dictionary with the following keys:
      - username: Optional username (or None)
      - password: Optional password (or None)
      - host: The Redis server hostname or IP address (or None for Unix socket)
      - port: The port number (default is 6379 for non-TLS and 6380 for TLS if not specified, or None for Unix socket)
      - db: The database index as an integer (default 0 if not specified)
      - use_tls: Boolean flag, True if the URL scheme is "rediss", False otherwise.
      - unix_socket_path: The Unix socket path (or None if not applicable)
      - query_params: Dictionary of query parameters (or empty dictionary if not present)
      - fragment: The fragment part of the URL (or None if not present)
      
    Raises:
      ValueError: If the URL scheme is not valid, if the host is missing,
                  or if the DB portion is not a valid integer.
    """
    parsed = urlparse(url)
    
    # Validate the scheme: must be either 'redis', 'rediss', 'redis+unix', or 'rediss+unix'
    if parsed.scheme not in ("redis", "rediss", "redis+unix", "rediss+unix"):
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}. Use 'redis://', 'rediss://', 'redis+unix://', or 'rediss+unix://'.")
    use_tls = parsed.scheme in ("rediss", "rediss+unix")
    
    # Handle Unix socket paths
    if parsed.scheme in ("redis+unix", "rediss+unix"):
        unix_socket_path = parsed.path
        host = None
        port = None
    else:
        unix_socket_path = None
        host = parsed.hostname
        
        # Ensure the host is present
        if not host:
            raise ValueError("Invalid URL: Host is missing.")
        
        # Determine the port: default port is 6379 for non-TLS, or 6380 for TLS if not provided.
        port = parsed.port if parsed.port else (6380 if use_tls else 6379)
    
    # Username and password are optional
    username = parsed.username
    password = parsed.password
    
    # Validate username and password for invalid characters
    if username and any(c in username for c in ':/@'):
        raise ValueError("Invalid characters in username.")
    if password and any(c in password for c in ':/@'):
        raise ValueError("Invalid characters in password.")
    
    # Parse the database number from the path.
    # The path should be of the form '/0' for DB index 0. Remove the leading '/'
    if parsed.path and len(parsed.path) > 1:
        try:
            db = int(parsed.path.lstrip("/"))
        except ValueError:
            raise ValueError(f"Invalid database number in URL path: '{parsed.path}'.")
    else:
        db = 0  # Default DB index
    
    # Parse query parameters and fragment
    query_params = parse_qs(parsed.query)
    fragment = parsed.fragment if parsed.fragment else None
    
    return {
        "username": username,
        "password": password,
        "host": host,
        "port": port,
        "db": db,
        "use_tls": use_tls,
        "unix_socket_path": unix_socket_path,
        "query_params": query_params,
        "fragment": fragment,
    }

# Testing on some sample URLs
if __name__ == "__main__":
    test_urls = [
        "redis://localhost/0",
        "redis://:secret@redis.example.com/2",
        "redis://user:secret@redis.example.com:6380/1",
        "rediss://user:secret@secure.redis.com/3",
        "redis+unix:///path/to/socket",
        "rediss+unix:///path/to/secure/socket",
        # Edge case: missing DB portion defaults to 0.
        "redis://redis.example.com",
        # URL with query parameters and fragment
        "redis://user:secret@redis.example.com:6379/1?param1=value1&param2=value2#fragment",
    ]

    for url in test_urls:
        try:
            result = parse_redis_url(url)
            print(f"Parsed URL: {url}")
            print(result)
            print("-" * 40)
        except ValueError as error:
            print(f"Error parsing '{url}': {error}")
