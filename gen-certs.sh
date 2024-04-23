#!/bin/bash
# refer: https://github.com/slackhq/simple-kubernetes-webhook/blob/main/dev/gen-certs.sh

echo "Please enter the IP address for the webhook server:"
echo "Note: This IP address must be accessible from the Kubernetes cluster"
echo -n "IP: "
read ip_address

if [[ $ip_address =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo
    echo ">> Generating certificates..."
    echo "IP address: $ip_address"
else
    echo "Invalid IP address"
    exit 1
fi

openssl genrsa -out ca.key 2048

openssl req -new -x509 -days 365 -key ca.key \
  -subj "/C=AU/CN=kubernetes-mutating-webhook-demo"\
  -out ca.crt

openssl req -newkey rsa:2048 -nodes -keyout server.key \
  -subj "/C=AU/CN=kubernetes-mutating-webhook-demo" \
  -out server.csr

openssl x509 -req \
  -extfile <(printf "subjectAltName=DNS:kubernetes-mutating-webhook-demo.default.svc,IP:${ip_address}") \
  -days 365 \
  -in server.csr \
  -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out server.crt

echo
#echo ">> Generating kube secrets..."
# kubectl create secret tls simple-kubernetes-webhook-tls \
#   --cert=server.crt \
#   --key=server.key \
#   --dry-run=client -o yaml \
#   > ./manifests/webhook/webhook.tls.secret.yaml

#echo
#echo ">> MutatingWebhookConfiguration caBundle:"
cat ca.crt | base64 | fold > caBundle.txt

test -d ./certs || mkdir ./certs
mv ca.crt ca.key ca.srl server.crt server.csr server.key ./certs