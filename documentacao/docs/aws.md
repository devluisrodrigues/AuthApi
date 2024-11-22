# Subindo a aplicação no AWS Elastic Kubernetes Service (EKS)

Para subir a aplicação no AWS EKS, é necessário ter uma conta na AWS e ter o `aws-cli` instalado e configurado.

### **Configuração do ambiente:**

- Crie um diretório para organizar os arquivos do projeto, por exemplo: `mkdir projeto-cloud`. E acesse o diretório criado: `cd projeto-cloud`

- Crie o cluster EKS com o comando:

```bash
eksctl create cluster --name projeto-cluster-fastapi --region us-east-2 --nodes 2 --node-type t3.small
```
> **Nota:** Por experiência própria, verifique os preços de cada região antes de criar o cluster, https://cloudprice.net/aws/regions. Nota do aluno que subiu o cluster em São Paulo (sa-east-1) e está refazendo o projeto para Ohio (us-east-2), pois ficou assustado com o preço.

O comando acima cria um cluster EKS com o nome `projeto-cluster-fastapi` na região `us-east-2` com 2 nodes com tamanho t3.small com uma VPC e subnets default.

Os nodes são instâncias EC2, que irão executar os containers da aplicação.

> **Nota:** Foram utilizadas máquinas t3.small por questões de custo e desempenho, para o projeto em questão, essas máquinas são suficientes. Porém, é possível utilizar máquinas com mais recursos.

> **Nota:** O EKS apresenta uma vantagem de escalabilidade, ou seja, é possível aumentar ou diminuir a quantidade de nodes conforme a necessidade, evitando gargalos na aplicação.

Espere a criação do cluster, pode demorar alguns minutos.

Após criar o cluster, execute o comando abaixo para configurar o `kubectl` para configurar o acesso ao cluster pelo CLI:

```bash
aws eks --region us-east-2 update-kubeconfig --name projeto-cluster-fastapi
```

Agora o `kubectl` está configurado para acessar o cluster `projeto-cluster-fastapi`. Assim, você pode analisar o que está acontecendo no cluster, como os nodes, pods, deployments, etc, pelo terminal.

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
fastapi-service   LoadBalancer   10.100.xxx.xxx   a7fa69d196c014e0390429e20fdb0087-758149223.us-east-2.elb.amazonaws.com   80:30309/TCP   2m27s
kubernetes        ClusterIP      10.100.xxx.xxx   <none>                                                                   443/TCP        23m
postgres          ClusterIP      10.100.xxx.xxx   <none>                                                                   5432/TCP       5m9s
```

Use o endereço `EXTERNAL-IP` para acessar a aplicação.

### **Endpoints da API:**

- É possível conferir o swagger da API acessando o endereço 
`http://a94c4a09f48814d65bb093ad15476d61-563405062.us-east-2.elb.amazonaws.com/docs` ou clickando em [swagger](http://a94c4a09f48814d65bb093ad15476d61-563405062.us-east-2.elb.amazonaws.com/docs)

Os endpoints da API são os mesmos da aplicação rodando localmente. E podem ser utilizados através dos links:

- **Post /registrar** : 

 `http://a94c4a09f48814d65bb093ad15476d61-563405062.us-east-2.elb.amazonaws.com/registrar`

 <!-- Curl Exemplo -->
```bash
curl -X 'POST' \
  'http://a94c4a09f48814d65bb093ad15476d61-563405062.us-east-2.elb.amazonaws.com/registrar' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "luis@teste.com",
    "nome": "luis testen",
    "senha": "123"
  }'
```

- **Post /login** : 

`http://a94c4a09f48814d65bb093ad15476d61-563405062.us-east-2.elb.amazonaws.com/login`

<!-- Curl Exemplo -->
```bash
curl -X POST http://a94c4a09f48814d65bb093ad15476d61-563405062.us-east-2.elb.amazonaws.com/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hwatermann@moedinha.ia",
    "senha": "123456"
  }'
```

- **Get /consultar** : 

 `http://a94c4a09f48814d65bb093ad15476d61-563405062.us-east-2.elb.amazonaws.com/consultar`

<!-- Curl Exemplo -->
```bash
curl -X GET http://a94c4a09f48814d65bb093ad15476d61-563405062.us-east-2.elb.amazonaws.com/consultar \
  -H "Authorization: Bearer SEU_TOKEN_JWT"
```

> **Nota:** Para obter o token JWT, é necessário se registrar e/ou logar na aplicação. O token JWT é retornado no corpo da resposta e tem duração de 10 minutos.

### Referências:

- [Como criar um cluster EKS na AWS](https://eksctl.io/usage/creating-and-managing-clusters/)

- [Documentação do EKS](https://docs.aws.amazon.com/eks/latest/userguide/getting-started-eksctl.html)

- [Como criar cluster Kubernetes EKS na AWS com EKSCTL](https://sidneiweber.com.br/como-criar-cluster-kubernetes-eks-na-aws-com-eksctl/ )

