# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Download AzCopy
wget https://aka.ms/downloadazcopy-v10-linux -O /tmp/downloadazcopy-v10-linux
# Expand Archive
tar -xvf /tmp/downloadazcopy-v10-linux -C /tmp
# Move AzCopy to the destination you want to store it
cp /tmp/azcopy_linux_amd64_*/azcopy /tmp/azcopy

mkdir /home/azureuser/.ldim_benchmark_cache
mkdir /home/azureuser/.ldim_benchmark_cache/datagen
# az storage fs directory download -f benchmark-cache --account-name masterthesisdata -s "datagen" -d "/home/azureuser/.ldim_benchmark_cache" --recursive --sas-token "${SAS_TOKEN}"

/tmp/azcopy copy "https://masterthesisdata.dfs.core.windows.net/benchmark-cache/datagen/synthetic-${DATA_FOLDER}${SAS_TOKEN}" /home/azureuser/.ldim_benchmark_cache/datagen --recursive



# Install Python
sudo apt install -y python3-pip
pip install ldimbenchmark

cat > /home/azureuser/benchmark.py <<EOF
${BENCHMARK_SCRIPT}
EOF

# sudo python3 /home/azureuser/benchmark.py
