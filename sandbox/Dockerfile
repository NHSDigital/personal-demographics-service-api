FROM node:12.18.0-alpine3.10

WORKDIR /app

COPY package*.json ./

RUN npm install --only=production

COPY src/ ./
COPY mocks/ mocks
RUN chmod -R a+x /app

USER nobody

# Entry point
CMD ["node", "app.js"]