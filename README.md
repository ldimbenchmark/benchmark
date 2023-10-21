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

Use the [cheapeast VM](https://azureprice.net/?_numberOfCores_min=16&_memoryInMB_min=256&_numberOfCores_max=32&sortField=linuxPrice&sortOrder=true), eg `Standard_D16as_v5` or `Standard_E16as_v5`, `Standard_FX24mds` depending on your memory requirements. 
