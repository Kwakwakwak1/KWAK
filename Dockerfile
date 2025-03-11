FROM node:14-alpine

WORKDIR /app

# Copy the package file and install dependencies
COPY package.json .
RUN npm install

# Copy the rest of your code
COPY . .

EXPOSE 3000

CMD ["npm", "start"]
