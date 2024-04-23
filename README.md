## k8s Mutating Admssion Webhook Demo
Python + FastAPI 开发的k8s Mutating Admssion Webhook Demo,实现给pod自动加上`foo=bar`的label

### 验证
1、使用minikube在本地启动一个k8s集群
```
$ minikube start --image-mirror-country=cn
```

2、本地启动一个webhook服务
```
# 创建python虚拟环境
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
# 根据提示输入IP，在./certs生成证书
$ bash gen-certs.sh
# 启动服务
$ python main.py 
```

3、修改webhook的配置文件
```
$ cat caBundle.txt
LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURVVENDQWptZ0F3SUJBZ0lVTkdzZlc2SzQxc2k3
...

$ vim deploy/pod-labeler-admissionWebhookConfig.yaml
  clientConfig:
    url: https://192.168.1.1:8000/mutate  # 把这里的IP换成你的本地IP
    caBundle: |
      # 这里替换成上面的caBundle.txt里面的内容，注意缩进
```
        
4、把admissionWebhookConfig更新到集群
```
$ kubectl apply -f deploy/pod-labeler-admissionWebhook.yaml
```

5、创建一个deployment，验证webhook是否生效
```
$ kubectl apply -f deploy/pod-test.yaml
# deploy里面是没有foo: bar这个label的
$ kubectl get deploy -oyaml |grep "labels:" -A 2
        labels:
          app: test-app
      spec:

# 但是pod里面有foo: bar这个label了
$ kubectl get pod -oyaml |grep "labels:" -A 2
    labels:
      app: test-app
      foo: bar
```

