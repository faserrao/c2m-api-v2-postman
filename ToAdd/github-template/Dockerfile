FROM node:18-alpine

# Install Newman and HTML reporter
RUN npm install -g newman newman-reporter-html

WORKDIR /tests
COPY postman /tests/postman
COPY lob_postman_collection_monitor_ready.json collection.json

# Default run (can override with docker run args)
ENTRYPOINT ["newman", "run", "collection.json", "--reporters", "cli,html", "--reporter-html-export", "report.html"]