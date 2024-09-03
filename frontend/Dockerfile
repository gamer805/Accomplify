# pull official base image
FROM node:17-alpine3.14

# set working directory
WORKDIR /app

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH

# install app dependencies
COPY package.json ./
COPY package-lock.json ./
COPY .npmrc ./
RUN npm install
RUN rm -f .npmrc

# add app
COPY . ./

# start app
EXPOSE 3000
CMD ["npm", "start"]