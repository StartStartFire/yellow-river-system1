# Stage 1: Build the Vue app
FROM docker.io/node:20-slim AS builder

WORKDIR /app

RUN apt-get update -y && apt-get install -y --no-install-recommends openssl && rm -rf /var/lib/apt/lists/*

COPY package.json package-lock.json ./
RUN npm ci --registry=https://mirrors.prod.eslab.org.cn/npm

COPY . .
RUN npm run build

# Stage 2: Serve static files with nginx
FROM docker.io/nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
