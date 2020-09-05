FROM nginx:alpine

COPY . /usr/share/nginx/html
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

WORKDIR /
ENTRYPOINT ["nginx","-g","daemon off;"]