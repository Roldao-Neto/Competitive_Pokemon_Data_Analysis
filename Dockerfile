FROM postgres:18

# The schema is created by the Python models in src/3-gold/models,
# not by SQL files baked into the image.

EXPOSE 5432
