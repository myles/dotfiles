# Return the LAN and WAN IP addresses for the current machine.

function ips() {
    echo "LAN: $(ifconfig | grep 'inet ' | grep -Fv 127.0.0.1 | awk '{print $2}' | xargs | sed -e 's/ /, /g')"
    echo "WAN: $(dig +short myip.opendns.com @resolver1.opendns.com)"
}
