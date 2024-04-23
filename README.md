[中文](./README-zh.md)

## k8s Mutating Admission Webhook Demo 
A Python + FastAPI developed k8s Mutating Admission Webhook demo that automatically adds the label foo=bar to pods.  

### Verification
1、Use minikube to start a local k8s cluster
```
$ minikube start
```

2、Start a webhook service locally
```
# Create a python virtual environment
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
# Follow the prompt to enter IP, generate certificates in ./certs
$ bash gen-certs.sh
# Start the service
$ python main.py 
```

3、Modify the webhook configuration file
```
$ cat caBundle.txt
LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURVVENDQWptZ0F3SUJBZ0lVTkdzZlc2SzQxc2k3
...

$ vim deploy/pod-labeler-admissionWebhookConfig.yaml
  clientConfig:
    url: https://192.168.1.1:8000/mutate  # Change this IP to your local IP
    caBundle: |
      # Replace here with the content from above caBundle.txt, pay attention to indentation
```

4、Update the admissionWebhookConfig to the cluster
```
$ kubectl apply -f deploy/pod-labeler-admissionWebhook.yaml
```

5、Create a deployment to verify if the webhook is effective
```
$ kubectl apply -f deploy/pod-test.yaml
# Inside deploy there isn't the foo: bar label
$ kubectl get deploy -oyaml |grep "labels:" -A 2
        labels:
          app: test-app
      spec:

# But now the pod has the foo: bar label
$ kubectl get pod -oyaml |grep "labels:" -A 2
    labels:
      app: test-app
      foo: bar
```

