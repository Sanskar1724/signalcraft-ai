FROM node:20-alpine AS build
WORKDIR /srv/web
COPY apps/web/package.json apps/web/package-lock.json* ./
RUN npm install
COPY apps/web .
RUN npm run build

FROM node:20-alpine
WORKDIR /srv/web
ENV NODE_ENV=production
COPY --from=build /srv/web ./
EXPOSE 3000
CMD ["npm", "start"]
