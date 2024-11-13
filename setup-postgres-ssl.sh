#!/bin/bash
# save as setup-ssl.sh

# remove existing directory
rm -rf postgres_ssl

# Create SSL directory
mkdir -p postgres_ssl
cd postgres_ssl


# Generate self signed certificate
openssl req -new -x509 -days 365 -noenc -outform PEM -text -out server.crt -keyout server.key -subj "/C=UK/ST=Lewisham/L=London/O=Pulse/CN=db"
cp server.crt root.crt


# Generate client certificate
openssl req -text -new -noenc -outform PEM -subj "/C=UK/ST=Lewisham/L=London/O=Pulse/CN=backend" -keyout client.key -out client.csr
openssl x509 -days 365 -text -req -outform PEM -CAcreateserial -in client.csr -CA root.crt -CAkey server.key -out client.crt

# Set proper permissions
chmod 600 *.key
chmod 644 *.crt

# Clean up intermediate files
rm *.csr *.srl

cd ..
