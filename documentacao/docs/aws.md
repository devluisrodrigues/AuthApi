# Subindo a aplicação no AWS Elastic Kubernetes Service (EKS)

Para subir a aplicação no AWS EKS, é necessário ter uma conta na AWS e ter o `aws-cli` instalado e configurado.

### **Configuração do ambiente:**

- Crie um diretório para organizar os arquivos do projeto, por exemplo: `mkdir projeto-cloud`. E acesse o diretório criado: `cd projeto-cloud`

- Crie o cluster EKS com o comando:

> **Nota:** Por experiência própria, verifique os preços de cada região antes de criar o cluster, https://cloudprice.net/aws/regions. Nota do aluno que subiu o cluster em São Paulo (sa-east-1) e está refazendo o projeto para Ohio (us-east-2), pois ficou assustado com o preço.

```bash
eksctl create cluster --name projeto-cluster --region us-east-2 --nodes 2
```

O comando acima cria um cluster EKS com o nome `projeto-cluster` na região `us-east-2` com 2 nodes com tamanho default m5.large com uma VPC e subnets default. Os nodes são instâncias EC2, que irão executar os containers da aplicação.

> **Nota:** O EKS apresenta uma vantagem de escalabilidade, ou seja, é possível aumentar ou diminuir a quantidade de nodes conforme a necessidade, evitando gargalos na aplicação.

Espere a criação do cluster, pode demorar alguns minutos.

Após criar o cluster, execute o comando abaixo para configurar o `kubectl` para acessar o cluster:

```bash
aws eks --region us-east-2 update-kubeconfig --name projeto-cluster
```

Agora o `kubectl` está configurado para acessar o cluster `projeto-cluster`. Assim, você pode analisar o que está acontecendo no cluster, como os nodes, pods, deployments, etc, pelo terminal.

Por exemplo, para listar os nodes do cluster, execute o comando:

```bash
kubectl get nodes
```

Para listar os pods, execute o comando:

```bash
kubectl get pods
```

Como ainda não há nenhum pod rodando, o comando acima não retornará nada.

### **Subindo a aplicação no EKS:**

- Crie o arquivo `db-deployment.yaml` com o seguinte conteúdo:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:17
        env:
          - name: POSTGRES_USER
            value: "COLOQUE_SEU_USUARIO_AQUI"
          - name: POSTGRES_PASSWORD
            value: "COLORQUE_SUA_SENHA_AQUI"
          - name: POSTGRES_DB
            value: "COLORQUE_O_NOME_DO_BANCO_AQUI"
        ports:
          - containerPort: 5432
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  ports:
    - port: 5432
  selector:
    app: postgres
```

- Em seguida, execute o comando:

```bash
kubectl apply -f db-deployment.yaml
```

O comando acima irá criar um deployment e um service para o banco de dados PostgreSQL.

- Em seguida, crie o arquivo `fastapi-deployment.yaml` com o seguinte conteúdo:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi
spec:
  replicas: 1
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: lasr2/authapi:latest
        env:
          - name: DATABASE_URL
            value: "postgresql://SEU_USUARIO:SUA_SENHA@postgres:5432/SEU_BANCO"
          - name: SECRET_KEY
            value: "INSIRA_SUA_CHAVE_SECRETA_AQUI"
        ports:
          - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 8080
  selector:
    app: fastapi
```

- Em seguida, execute o comando:

```bash
kubectl apply -f fastapi-deployment.yaml
```

O comando acima irá criar um deployment e um service para a aplicação FastAPI.

- Para verificar se os pods estão rodando, execute o comando:

```bash
kubectl get pods
```

A resposta seguirá o modelo abaixo:

```bash
NAME                       READY   STATUS    RESTARTS   AGE
fastapi-xxxxxxxxxx-xxxxx   1/1     Running   0          16s
postgres-xxxxxxxxx-xxxxx   1/1     Running   0          2m58s
```

Por questão de privacidade, os nomes dos pods foram substituídos por `xxxxxxxxxx-xxxxx`.

Por fim, execute o comando:

```bash
kubectl get services
```

Caso tudo tenha funcionado, a resposta será:

```bash
NAME              TYPE           CLUSTER-IP       EXTERNAL-IP                                                              PORT(S)        AGE
fastapi-service   LoadBalancer   10.100.xxx.xxx   ab757c16c8f5b4ffdae63bd6ff19a8a6-759760828.us-east-2.elb.amazonaws.com   80:30309/TCP   2m27s
kubernetes        ClusterIP      10.100.xxx.xxx   <none>                                                                   443/TCP        23m
postgres          ClusterIP      10.100.xxx.xxx   <none>                                                                   5432/TCP       5m9s
```

Use o endereço `EXTERNAL-IP` para acessar a aplicação.

### **Endpoints da API:**

- É possível conferir o swagger da API acessando o endereço 
`http://ab757c16c8f5b4ffdae63bd6ff19a8a6-759760828.us-east-2.elb.amazonaws.com/docs` ou clickando em [swagger](http://ab757c16c8f5b4ffdae63bd6ff19a8a6-759760828.us-east-2.elb.amazonaws.com/docs).

Os endpoints da API são os mesmos da aplicação rodando localmente. E podem ser utilizados através dos links:

- **Post /registrar** : 

 `http://ab757c16c8f5b4ffdae63bd6ff19a8a6-759760828.us-east-2.elb.amazonaws.com/registrar`

  [Atalho para o link de registrar](http://ab757c16c8f5b4ffdae63bd6ff19a8a6-759760828.us-east-2.elb.amazonaws.com/registrar)

- **Post /login** : 

`http://ab757c16c8f5b4ffdae63bd6ff19a8a6-759760828.us-east-2.elb.amazonaws.com/login`

[Atalho para o link de login](http://ab757c16c8f5b4ffdae63bd6ff19a8a6-759760828.us-east-2.elb.amazonaws.com/login)

- **Get /consultar** : 

 `http://ab757c16c8f5b4ffdae63bd6ff19a8a6-759760828.us-east-2.elb.amazonaws.com/consultar`

[Atalho para o link de consultar](http://ab757c16c8f5b4ffdae63bd6ff19a8a6-759760828.us-east-2.elb.amazonaws.com/consultar)

### Referências:

- [Documentação do EKS](https://docs.aws.amazon.com/eks/latest/userguide/getting-started-eksctl.html)

- [Como criar cluster Kubernetes EKS na AWS com EKSCTL](https://sidneiweber.com.br/como-criar-cluster-kubernetes-eks-na-aws-com-eksctl/ )

