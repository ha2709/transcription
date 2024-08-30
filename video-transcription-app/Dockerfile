# video-transcription-app/Dockerfile
# Use the official Node.js image.
FROM node:16

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
COPY package*.json ./

RUN npm install

# Bundle app source
COPY . .

# Expose the port on which the app will run
EXPOSE 3000

# Start the React app
CMD ["npm", "start"]
