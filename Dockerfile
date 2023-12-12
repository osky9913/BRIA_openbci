# Use the official pgAdmin image
FROM dpage/pgadmin4

# Set environment variables (change these values according to your needs)
ENV PGADMIN_DEFAULT_EMAIL=admin@example.com
ENV PGADMIN_DEFAULT_PASSWORD=admin

# Expose the port pgAdmin runs on
EXPOSE 80

# Run pgAdmin
ENTRYPOINT ["/entrypoint.sh"]
CMD ["pgadmin4"]
