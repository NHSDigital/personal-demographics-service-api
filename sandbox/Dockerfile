FROM node:20.12.1-alpine3.18

WORKDIR /app

COPY package*.json ./

RUN npm install --only=production

COPY src/ ./
COPY mocks/ mocks
RUN chmod -R a+x /app

USER nobody

# Entry point
CMD ["node", "app.js"]