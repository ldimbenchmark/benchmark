# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add Microsoft Repo
# curl -sSL https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc
# sudo apt-add-repository -y https://packages.microsoft.com/ubuntu/22.04/prod
# sudo apt-get update
# sudo apt-get install -y fuse3 blobfuse2

# Install azure-cli
sudo apt-get update
sudo apt-get install ca-certificates curl apt-transport-https lsb-release gnupg
sudo mkdir -p /etc/apt/keyrings
curl -sLS https://packages.microsoft.com/keys/microsoft.asc |
    gpg --dearmor |
    sudo tee /etc/apt/keyrings/microsoft.gpg > /dev/null
sudo chmod go+r /etc/apt/keyrings/microsoft.gpg
AZ_REPO=$(lsb_release -cs)
echo "deb [arch=`dpkg --print-architecture` signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" |
    sudo tee /etc/apt/sources.list.d/azure-cli.list

sudo apt-get update
sudo apt-get install azure-cli

 
#Download AzCopy
wget https://aka.ms/downloadazcopy-v10-linux -O /tmp/downloadazcopy-v10-linux
#Expand Archive
tar -xvf /tmp/downloadazcopy-v10-linux -C /tmp
# Remove existing AzCopy version
rm /home/azureuser/bin/azcopy
#Move AzCopy to the destination you want to store it
cp /tmp/azcopy_linux_amd64_*/azcopy /home/azureuser/bin/

# # Configure https://github.com/Azure/azure-storage-fuse
# cat > /home/azureuser/blobfuse.yaml <<EOF
# file_cache:
#   path: /home/azureuser/tempcache
#   timeout-sec: 120
#   max-size-mb: 4096

# attr_cache:
#   timeout-sec: 7200

# azstorage:
#   type: block
#   sas: ${SAS_TOKEN}
#   account-name: masterthesisdata
#   mode: sas
#   container: benchmark-cache
# EOF

# mkdir /blobmnt
# mkdir /mnt/blobfusetmp
# sudo blobfuse2 /blobmnt --tmp-path=/mnt/blobfusetmp --config-file=/home/azureuser/blobfuse.yaml

mkdir /home/azureuser/.ldim_benchmark_cache
mkdir /home/azureuser/.ldim_benchmark_cache/datagen
# cp -r /blobmnt/datagen/* /home/azureuser/.ldim_benchmark_cache/datagen
az storage fs directory download -f benchmark-cache --account-name masterthesisdata -s "datagen" -d "/home/azureuser/.ldim_benchmark_cache" --recursive --sas-token "${SAS_TOKEN}"


# Install Python
sudo apt install -y python3-pip
pip install ldimbenchmark

cat > /home/azureuser/benchmark.py <<EOF
${BENCHMARK_SCRIPT}
EOF

# sudo python3 /home/azureuser/benchmark.py
