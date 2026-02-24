# ─── Development ──────────────────────────
FROM node:22-alpine AS dev

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]

# ─── Production ───────────────────────────
FROM node:22-alpine AS builder

WORKDIR /app

ARG NEXT_PUBLIC_API_URL=https://bloom.nobleblocks.com
ARG NEXT_PUBLIC_WS_URL=wss://bloom.nobleblocks.com
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_WS_URL=$NEXT_PUBLIC_WS_URL

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:22-alpine AS production

WORKDIR /app

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000

CMD ["node", "server.js"]
