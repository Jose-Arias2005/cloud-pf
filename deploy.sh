#!/bin/bash

echo "Desplegando servicio general"
sls deploy

# Lista de directorios donde están los proyectos Serverless
services=("api-usuarios" "api-cine" "api-peliculas" "api-proyecciones" "api-reserva" "api-visitas")

# Recorrer cada directorio y ejecutar el despliegue
for service in "${services[@]}"
do
    echo "Desplegando servicio: $service"
    
    # Cambiar al directorio del servicio
    cd $service || exit
    
    # Ejecutar el despliegue con Serverless
    sls deploy --stage prod --region us-east-1
    
    # Volver al directorio original
    cd ..
done
