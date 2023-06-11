# benchmark

```
terraform init
terraform apply

ssh -i private.key -o StrictHostKeyChecking=no $(terraform output -raw host)
scp -r -i private.key -o StrictHostKeyChecking=no ./benchmark-normal-grid.py $(terraform output -raw host):/home/azureuser/benchmark.py
tmux new -s "benchmark" python benchmark.py

python benchmark.py > allout.txt 2>&1

terraform destroy
```
