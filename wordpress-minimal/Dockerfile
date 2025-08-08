# Use official WordPress image with Apache
FROM wordpress:php8.3-apache

# Install system dependencies (optional, e.g. for plugins/themes)
RUN apt-get update && apt-get install -y \
    less \
    vim \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Enable Apache mod_rewrite (WordPress permalinks)
RUN a2enmod rewrite

# Copy site code into container
COPY . /var/www/html/

# Set recommended file permissions
RUN chown -R www-data:www-data /var/www/html

# Copy custom wp-config.php if you have one
# COPY wordpress/wp-config.php /var/www/html/wp-config.php

# Copy all WordPress files (if not using the default image volume)
# COPY wordpress/ /var/www/html/

# Set recommended file permissions (optional, for plugins/themes)
# RUN chown -R www-data:www-data /var/www/html

# Expose port 80
EXPOSE 80

# Start Apache (default CMD from base image)
CMD ["apache2-foreground"]
