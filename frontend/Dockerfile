FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
# Rewrite hedefi derleme sırasında manifest'e yazılır.
ARG API_URL=http://backend:8000
ENV API_URL=$API_URL
RUN npm run build

FROM node:22-alpine AS run
WORKDIR /app
# Model kartı sayfası veriyi sunucu tarafında çeker.
ARG API_URL=http://backend:8000
ENV API_URL=$API_URL \
    NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0
RUN adduser -D -u 10001 app
COPY --from=build --chown=app /app/.next/standalone ./
COPY --from=build --chown=app /app/.next/static ./.next/static
COPY --from=build --chown=app /app/public ./public
USER app
EXPOSE 3000
CMD ["node", "server.js"]
