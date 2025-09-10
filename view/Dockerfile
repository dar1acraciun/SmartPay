FROM node:18-alpine

WORKDIR /view

COPY package*.json ./
RUN rm -rf node_modules package-lock.json
RUN npm install
RUN npm install html2canvas jspdf
RUN npm install axios
RUN npm install react-chartjs-2 chart.js

COPY . .

EXPOSE 8080

CMD ["npm", "run", "dev"]