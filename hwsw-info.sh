#!/bin/bash

#	------------------------------------------
#	Gets hardware info and outputs into Json
#	------------------------------------------

#	Pre-requisites:
#	- Must run as root
#	- amdmeminfo (https://github.com/Zuikkis/amdmeminfo)
#	- nvidia-smi

#	------------------------------------------
#	ToDo:
#	- WLAN AP has extra stuff at the end on m1
#	- WLAN / ETH Connected info is incorrect on m1
#	------------------------------------------

NUM_NVIDIA=0
NUM_AMD=0

#	Operating System Info
OS_NAME=$(cat /etc/*release | grep -E 'DISTRIB_DESCRIPTION' | sed -r 's/.+=|"//g')
OS_KERNEL=$(uname -r)

#	Motherboard Info
MB_MANU=$(dmidecode | grep -A2 'Base' | grep 'Manu' | sed -r s/.+:.//)
MB_MODEL=$(dmidecode | grep -A2 'Base' | grep 'Produ' | sed -r s/.+:.//)

#	Network Info
LAN_IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1')
WLAN_AP=$(iwconfig | grep 'ESSID' | sed -r 's/.+ESSID:|"|\s+$//g')
WLAN_CONN=$(lshw -class network | grep -A6 'Wireless' | grep 'configuration' | sed 's/configuration: //' | awk '{print $6}' | sed -r 's/.+=//')
ETH_CONN=$(lshw -class network | grep -A11 'Ethernet' | grep 'configuration' | sed 's/configuration: //' | awk '{print $7}' | sed -r 's/.+=//')

#	CPU and RAM Info
CPU_TYPE=$(lscpu | grep 'Model name' | sed -r 's/.+: +//')
CORE_NUM=$(lscpu | grep "^CPU(s):" | sed -r 's/.+:. +//')
CPU_NUM=$(lscpu | grep "^Socket(s):" | sed -r 's/.+:. +//')
RAM=$(dmidecode --type memory | grep -E 'Size' | grep -E 'MB' | sed -r 's/.+: //')

#	GPU Info
NUM_NVIDIA=$(lspci | grep 'VGA' | grep -E 'NVIDIA|GTX' | wc -l)
NUM_AMD=$(lspci | grep 'VGA' | grep -E 'Advanced Micro Devices|RX' | wc -l)

echo -e "{"
echo -e "   \"LanIp\": \"$LAN_IP\","
echo -e "   \"WlanAp\": \"$WLAN_AP\","
echo -e "   \"WlanConnected\": \"$WLAN_CONN\","
echo -e "   \"EthConnected\": \"$ETH_CONN\","
echo -e "   \"OperatingSystem\": \"$OS_NAME\","
echo -e "   \"OsKernel\": \"$OS_KERNEL\","
echo -e "   \"Motherboard\": \"$MB_MANU $MB_MODEL\","
echo -e "   \"CpuType\": \"$CPU_TYPE\","
echo -e "   \"CpuCores\": \"$CORE_NUM\","
echo -e "   \"CpuNum\": \"$CPU_NUM\","
echo -e "   \"Ram\": \"$RAM\","
echo -e "   \"NumNvidiaGpu\": \"$NUM_NVIDIA\","
echo -e "   \"NumAmdGpu\": \"$NUM_AMD\","

if [ $NUM_NVIDIA -gt 0 ];then

   echo -e "   \"NvidiaGpus\": ["

   i=0
   nvidia-smi -L | while read line; do
      [[ $i+1 -lt $NUM_NVIDIA ]] && LINE_END=',' || LINE_END=''
      echo "      \"$line\"$LINE_END";
      let i+=1
   done
   echo -e "   ],"
else
   echo -e "   \"NvidiaGpus\": [],"
fi

if [ $NUM_AMD -gt 0 ];then

   echo -e "   \"AmdGpus\": ["

   i=0
   amdmeminfo -q -s -L | while read line; do
      [[ $i+1 -lt $NUM_NVIDIA ]] && LINE_END=',' || LINE_END=''
      echo "      \"$line\"$LINE_END";
      let i+=1
   done
   echo -e "   ]"
else
   echo -e "   \"AmdGpus\": []"
fi

echo -e "}"
