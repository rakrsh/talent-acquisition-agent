# Build argument for version
ARG VERSION=dev

FROM node:20-slim AS builder

WORKDIR /app

# Set version label for builder stage
LABEL org.opencontainers.image.version="${VERSION}"

COPY services/web/package*.json ./
RUN npm install

COPY services/web/ .
RUN npm run build

FROM node:20-slim AS runner

# Set version label
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.title="Talent Acquisition Agent - Web Service"

WORKDIR /app
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

# Pass version to container
ENV VERSION=${VERSION}

EXPOSE 3000

CMD ["npm", "start"]
