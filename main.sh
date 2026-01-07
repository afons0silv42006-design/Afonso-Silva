#!/bin/bash

V='\033[0;32m'
R='\033[0;31m'
F='\033[0m' 

echo "--- Relatorio do monitoramento do pc ($(date +%H:%M:%S)) ---"

c=$(wmic cpu get loadpercentage | grep -o '[0-9]\+' | head -1)
echo -e "CPU: ${V}${c}%${F}"

rl=$(wmic os get freephysicalmemory | grep -o '[0-9]\+')
rt=$(wmic computersystem get totalphysicalmemory | grep -o '[0-9]\+')

t=$((rt / 1024 / 1024))
l=$((rl / 1024))
u=$((t - l))
p=$((u * 100 / t))

echo -e "RAM: ${V}${u}MB / ${t}MB (${p}%)${F}"

d=$(df -h /c | tail -1 | awk '{print $5}' | cut -d'%' -f1)
echo -e "Disco C: ${V}${d}% usado${F}"

echo "------------------------------------------"

if [ $p -gt 80 ]; then
    echo -e "${R}A ram esta quase cheia!${F}"
fi

if [ $d -gt 90 ]; then
    echo -e "${R}Cuidado: Ram esta a atingir o limite!${F}"
fi

echo "Relatorio Finalizado."
