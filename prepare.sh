# See here for troubleshooting: https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/troubleshoot

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Download AzCopy
wget https://aka.ms/downloadazcopy-v10-linux -O /tmp/downloadazcopy-v10-linux
# Expand Archive
tar -xvf /tmp/downloadazcopy-v10-linux -C /tmp
# Move AzCopy to the destination you want to store it
cp /tmp/azcopy_linux_amd64_*/azcopy /tmp/azcopy

if [ $BENCHMARK_TYPE = "normal" ]
then
        echo "Preparing for Normal Benchmark"
        /tmp/azcopy copy "https://masterthesisdata.dfs.core.windows.net/benchmark-cache/${DATA_FOLDER}${SAS_TOKEN}" /home/azureuser/datasets --recursive
else
        echo "Preparing for Complexity Benchmark"
        mkdir /home/azureuser/.ldim_benchmark_cache
        mkdir /home/azureuser/.ldim_benchmark_cache/datagen

        /tmp/azcopy copy "https://masterthesisdata.dfs.core.windows.net/benchmark-cache/${DATA_FOLDER}${SAS_TOKEN}" /home/azureuser/.ldim_benchmark_cache/datagen --recursive
fi




# Install Python
sudo apt install -y python3-pip
pip install ldimbenchmark

# sudo python3 /home/azureuser/benchmark.py
