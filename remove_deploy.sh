#!/bin/bash

echo "Eliminando servicio general"
sls remove 

# Lista de directorios donde están los proyectos Serverless
services=("api-usuarios" "api-cine" "api-peliculas" "api-proyecciones" "api-reserva" "api-visitas")

# Recorrer cada directorio y ejecutar el remove
for service in "${services[@]}"
do
    echo "Eliminando servicio: $service"
    
    # Cambiar al directorio del servicio
    cd $service || exit
    
    # Ejecutar el remove con Serverless
    sls remove 
    
    # Volver al directorio original
    cd ..
done
