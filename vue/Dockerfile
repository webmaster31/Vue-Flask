ARG env

FROM node:14.17.6 as base-stage

FROM base-stage as development-stage
WORKDIR /app
COPY package.json ./
RUN npm install 
COPY . .
EXPOSE 8080
CMD ["npm", "run", "serve"]
ENV VAR=development

FROM base-stage as build-stage
WORKDIR /app
COPY package.json ./
RUN npm install 
COPY . .
RUN npm run build

FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
ENV VAR=production
CMD ["nginx", "-g", "daemon off;"]

FROM ${env}-stage as final
RUN echo "Built ${VAR} container"
