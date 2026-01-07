#!/bin/bash

echo "Data/Hora: $(date)"

CPU_LOAD=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
echo -e "Uso de CPU: ${VERDE}${CPU_LOAD}%${RESET}"

MEM_TOTAL=$(free -m | awk '/Mem:/ {print $2}')
MEM_USADA=$(free -m | awk '/Mem:/ {print $3}')
MEM_PERC=$(( MEM_USADA * 100 / MEM_TOTAL ))

echo -e "Memoria RAM: ${VERDE}${MEM_USADA}MB / ${MEM_TOTAL}MB (${MEM_PERC}%)${RESET}"

DISCO_PERC=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
echo -e "Espaço em Disco (/): ${VERDE}${DISCO_PERC}% usado${RESET}"

echo "--------------------------------------------"
if [ "$MEM_PERC" -gt 80 ]; then
    echo -e "${VERMELHO} ALERTA: Uso de Memoria RAM acima de 80%${RESET}"
fi

if [ "$DISCO_PERC" -gt 90 ]; then
    echo -e "${VERMELHO} ALERTA: Pouco espaço em disco disponivel${RESET}"
fi

echo "Verificação finalizada."
