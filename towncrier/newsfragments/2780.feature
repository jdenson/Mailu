Feature: Redis Sentinel, Authentication & TLS Support

Mailu now accepts advanced Redis connection URLs for REDIS_RATELIMIT, REDIS_QUOTA, and REDIS_FUZZDB, e.g.:
  redis://[{username}:{password}]@{host}[:{port}]/{db},
including TLS support via the rediss:// scheme.
