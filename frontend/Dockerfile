# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copier les fichiers de package
COPY package*.json ./

# Installer les dépendances
RUN npm ci --only=production

# Copier le code source
COPY . .

# Construire l'application
ARG REACT_APP_API_URL=http://localhost:8000
ENV REACT_APP_API_URL=$REACT_APP_API_URL
RUN npm run build

# Production stage
FROM nginx:alpine

# Copier la configuration nginx personnalisée
COPY docker/nginx/frontend.conf /etc/nginx/conf.d/default.conf

# Copier les fichiers buildés
COPY --from=build /app/build /usr/share/nginx/html

# Exposer le port
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Commande par défaut
CMD ["nginx", "-g", "daemon off;"]
