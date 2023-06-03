# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add Microsoft Repo
curl -sSL https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc
sudo apt-add-repository -y https://packages.microsoft.com/ubuntu/22.04/prod
sudo apt-get update
sudo apt-get install -y fuse3 blobfuse2

# az storage blob directory download -c benchmark-cache --account-name masterthesisdata -s "datagen" -d "/home/azureuser/.ldim_benchmark_cache/datagen" --recursive --sas-token ${SAS_TOKEN}

# Configure https://github.com/Azure/azure-storage-fuse
cat > /home/azureuser/blobfuse.yaml <<EOF
file_cache:
  path: /home/azureuser/tempcache
  timeout-sec: 120
  max-size-mb: 4096

attr_cache:
  timeout-sec: 7200

azstorage:
  type: block
  sas: ${SAS_TOKEN}
  account-name: masterthesisdata
  mode: sas
  container: benchmark-cache
EOF

mkdir /blobmnt
mkdir /mnt/blobfusetmp
sudo blobfuse2 /blobmnt --tmp-path=/mnt/blobfusetmp --config-file=/home/azureuser/blobfuse.yaml

mkdir /home/azureuser/.ldim_benchmark_cache
mkdir /home/azureuser/.ldim_benchmark_cache/datagen
cp -r /blobmnt/datagen/* /home/azureuser/.ldim_benchmark_cache/datagen



# Install Python
sudo apt install -y python3-pip
pip install ldimbenchmark

cat > /home/azureuser/benchmark.py <<EOF
${BENCHMARK_SCRIPT}
EOF

# sudo python3 /home/azureuser/benchmark.py
