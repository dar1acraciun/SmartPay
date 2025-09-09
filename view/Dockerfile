FROM node:18-alpine

WORKDIR /view

COPY package*.json ./
RUN npm install
RUN npm install html2canvas jspdf

COPY . .

EXPOSE 8080

CMD ["npm", "run", "dev"]