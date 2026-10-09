FROM node:20-slim

WORKDIR /app

# 依赖
COPY package.json package-lock.json ./
RUN npm ci

# 源码与构建
COPY . .
RUN npm run build

ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000

CMD ["npm", "start"]
