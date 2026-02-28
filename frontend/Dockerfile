# syntax=docker/dockerfile:1

# -----------------------------------------------------------------------------
# Stage 1: deps
# Installs production and development dependencies.
# Separated so this layer is cached and only rebuilds when package files change.
# -----------------------------------------------------------------------------
FROM node:22-alpine AS deps

RUN apk add --no-cache libc6-compat

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn install --frozen-lockfile


# -----------------------------------------------------------------------------
# Stage 2: builder
# Builds the Next.js application using the installed dependencies.
# The standalone output mode copies only the required runtime files.
# -----------------------------------------------------------------------------
FROM node:22-alpine AS builder

WORKDIR /app

# Copy dependencies from the deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy all source files
COPY . .

# Disable Next.js telemetry during the build
ENV NEXT_TELEMETRY_DISABLED=1

RUN yarn build


# -----------------------------------------------------------------------------
# Stage 3: runner
# Minimal production image — contains only the standalone server output,
# static assets, and public files. No node_modules or source code.
# -----------------------------------------------------------------------------
FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create a non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy the standalone server output
COPY --from=builder /app/.next/standalone ./

# Copy static assets generated during build
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Copy the public directory
COPY --from=builder /app/public ./public

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Start the standalone Next.js server
CMD ["node", "server.js"]
