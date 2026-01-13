# --- 1. BUILD STAGE ---
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# --- 2. DEVELOPMENT STAGE ---
FROM node:20-alpine AS development
WORKDIR /app
ENV NODE_ENV development
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

# --- 3. RUNNER STAGE ---
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production

# --- 2.1 PERMISSIONS ---
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# --- 2.2 ASSETS ---
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# --- 2.3 STARTUP ---
CMD ["node", "server.js"]
