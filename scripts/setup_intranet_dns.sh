#!/bin/bash
DNS_TO_ADD="nameserver 10.205.248.11"
RESOLV_CONF="/etc/resolv.conf"

if grep -qF "$DNS_TO_ADD" "$RESOLV_CONF"; then
    echo "'$DNS_TO_ADD' already exists. No changes needed."
else
    echo "Adding '$DNS_TO_ADD' to $RESOLV_CONF."

    TMP_FILE=$(mktemp)
    echo "$DNS_TO_ADD" > "$TMP_FILE"
    cat "$RESOLV_CONF" >> "$TMP_FILE"
    cat "$TMP_FILE" > "$RESOLV_CONF"
    rm "$TMP_FILE"

    echo "$RESOLV_CONF has been updated:"
    cat "$RESOLV_CONF"
fi

# curl -fsSL "https://dd-ai-service.eastmoney.com/aip-files/f/sh/setup_intranet_dns.sh" | tr -d '\r' | bash