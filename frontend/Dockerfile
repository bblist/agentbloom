FROM node:22-alpine

WORKDIR /app

# Dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy project
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
