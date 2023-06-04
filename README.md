# benchmark


```
terraform init
terraform apply

ssh -i private.key -o StrictHostKeyChecking=no $(terraform output -raw host)

terraform destroy
```

# TODO

Add Docker Methods for benchmark of ram and cpu?